from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.schemas import FeedbackSubmit, FeedbackResponse
from app.models.database import UserFeedback, User, Diagram, ValidatedInput
from app.ml.learning_system import FeedbackLearningSystem
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/feedback", tags=["feedback"])
learning_system = FeedbackLearningSystem()


@router.post("/", response_model=FeedbackResponse)
async def submit_feedback(
    feedback: FeedbackSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit feedback on a diagram or validation result.
    
    The system learns from this feedback to improve future validations.
    """
    # Validate that diagram or input exists
    if feedback.diagram_id:
        diagram = db.query(Diagram).filter(
            Diagram.id == feedback.diagram_id
        ).first()
        if not diagram:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Diagram not found"
            )
    
    # Store feedback
    user_feedback = UserFeedback(
        input_id=feedback.input_id,
        diagram_id=feedback.diagram_id,
        feedback_type=feedback.feedback_type,
        feedback_text=feedback.feedback_text,
        diagram_quality_rating=feedback.diagram_quality_rating,
        was_helpful=feedback.was_helpful,
        user_id=current_user.id
    )
    
    db.add(user_feedback)
    db.commit()
    db.refresh(user_feedback)
    
    # Learn from feedback if it's a correction or approval
    if feedback.feedback_type in ['correction', 'approval', 'invalid']:
        if feedback.diagram_id:
            diagram = db.query(Diagram).filter(
                Diagram.id == feedback.diagram_id
            ).first()
            
            if diagram:
                # Map feedback type to validation feedback
                feedback_map = {
                    'approval': 'valid',
                    'correction': 'needs_improvement',
                    'invalid': 'invalid'
                }
                
                learning_system.learn_from_feedback(
                    input_text=diagram.input_text,
                    user_feedback=feedback_map.get(feedback.feedback_type, 'needs_improvement'),
                    generated_diagram=diagram.mermaid_code,
                    pattern_type=diagram.diagram_type,
                    user_id=current_user.id,
                    db=db
                )
    
    return user_feedback


@router.get("/stats")
async def get_feedback_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get learning system statistics.
    """
    stats = learning_system.get_learning_stats(db)
    return stats

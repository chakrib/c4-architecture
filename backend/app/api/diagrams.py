from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.schemas import (
    DiagramGenerateRequest,
    DiagramGenerateResponse,
    DiagramResponse,
    DiagramListResponse
)
from app.models.database import Diagram, User
from app.services.diagram_service import DiagramService
from app.api.auth import get_current_user

router = APIRouter(prefix="/api/diagrams", tags=["diagrams"])
diagram_service = DiagramService()


@router.post("/generate", response_model=DiagramGenerateResponse)
async def generate_diagram(
    request: DiagramGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate a C4 diagram from solution overview text.
    
    - Validates input using rule-based and ML validation
    - Generates diagram using Claude AI
    - Optionally saves to database
    - Returns Mermaid code and validation results
    """
    try:
        result = await diagram_service.generate_diagram(
            request=request,
            user_id=current_user.id,
            db=db
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate diagram: {str(e)}"
        )


@router.get("/", response_model=DiagramListResponse)
async def list_diagrams(
    page: int = 1,
    page_size: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List user's diagrams with pagination.
    """
    skip = (page - 1) * page_size
    
    diagrams = db.query(Diagram).filter(
        Diagram.user_id == current_user.id
    ).order_by(
        Diagram.created_at.desc()
    ).offset(skip).limit(page_size).all()
    
    total = db.query(Diagram).filter(
        Diagram.user_id == current_user.id
    ).count()
    
    return DiagramListResponse(
        diagrams=diagrams,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{diagram_id}", response_model=DiagramResponse)
async def get_diagram(
    diagram_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific diagram by ID.
    """
    diagram = db.query(Diagram).filter(
        Diagram.id == diagram_id,
        Diagram.user_id == current_user.id
    ).first()
    
    if not diagram:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagram not found"
        )
    
    return diagram


@router.delete("/{diagram_id}")
async def delete_diagram(
    diagram_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a diagram.
    """
    diagram = db.query(Diagram).filter(
        Diagram.id == diagram_id,
        Diagram.user_id == current_user.id
    ).first()
    
    if not diagram:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Diagram not found"
        )
    
    db.delete(diagram)
    db.commit()
    
    return {"message": "Diagram deleted successfully"}

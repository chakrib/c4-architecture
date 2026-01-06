from sqlalchemy.orm import Session
from app.models.database import ValidatedInput, UserFeedback, LearnedPattern
from app.ml.semantic_validator import SemanticValidator
from datetime import datetime
from typing import Optional
import numpy as np


class FeedbackLearningSystem:
    """
    Continuous learning system that improves from user feedback.
    """
    
    def __init__(self):
        self.semantic_validator = SemanticValidator()
        self.retraining_threshold = 50  # Retrain after 50 new feedback items
    
    def learn_from_feedback(
        self,
        input_text: str,
        user_feedback: str,
        generated_diagram: str,
        pattern_type: Optional[str],
        user_id: int,
        db: Session
    ) -> ValidatedInput:
        """
        Store validated input with feedback for learning.
        """
        # Generate embedding
        embedding = self.semantic_validator.encode_text(input_text)
        
        # Calculate validation score based on feedback
        score_map = {
            'valid': 1.0,
            'needs_improvement': 0.7,
            'invalid': 0.0
        }
        validation_score = score_map.get(user_feedback, 0.5)
        
        # Store in database
        validated_input = ValidatedInput(
            input_text=input_text,
            embedding=embedding.tolist(),  # Convert numpy array to list for pgvector
            validation_score=validation_score,
            user_feedback=user_feedback,
            generated_diagram=generated_diagram,
            pattern_type=pattern_type,
            user_id=user_id
        )
        
        db.add(validated_input)
        db.commit()
        db.refresh(validated_input)
        
        # Check if we should update patterns
        self._update_patterns(input_text, pattern_type, db)
        
        # Check if retraining is needed
        if self._should_retrain(db):
            self._trigger_retraining(db)
        
        return validated_input
    
    def learn_from_correction(
        self,
        original_input: str,
        corrected_input: str,
        user_id: int,
        db: Session
    ) -> dict:
        """
        Learn when user corrects/improves their input.
        Stores both versions to learn what makes a good input.
        """
        # Store original as needs_improvement
        self.learn_from_feedback(
            input_text=original_input,
            user_feedback='needs_improvement',
            generated_diagram='',
            pattern_type=None,
            user_id=user_id,
            db=db
        )
        
        # Store corrected as valid
        corrected_validated = self.learn_from_feedback(
            input_text=corrected_input,
            user_feedback='valid',
            generated_diagram='',
            pattern_type=None,
            user_id=user_id,
            db=db
        )
        
        return {
            'learned': True,
            'message': 'Thank you! The system will learn from this correction.'
        }
    
    def _update_patterns(
        self,
        input_text: str,
        pattern_type: Optional[str],
        db: Session
    ):
        """
        Update learned patterns based on new validated input.
        """
        if not pattern_type:
            return
        
        # Get or create pattern
        pattern = db.query(LearnedPattern).filter(
            LearnedPattern.pattern_name == pattern_type
        ).first()
        
        if pattern:
            # Update existing pattern
            pattern.usage_count += 1
            pattern.last_updated = datetime.utcnow()
            
            # Add to example inputs if not too many
            if len(pattern.example_inputs or []) < 10:
                examples = pattern.example_inputs or []
                if input_text not in examples:
                    examples.append(input_text[:200])  # Store first 200 chars
                    pattern.example_inputs = examples
            
            # Update confidence based on usage
            pattern.confidence_score = min(
                1.0,
                0.5 + (pattern.usage_count * 0.01)  # Increases with usage
            )
        else:
            # Create new pattern
            keywords = self._extract_keywords(input_text)
            pattern = LearnedPattern(
                pattern_name=pattern_type,
                keywords=keywords,
                example_inputs=[input_text[:200]],
                confidence_score=0.5,
                usage_count=1
            )
            db.add(pattern)
        
        db.commit()
    
    def _extract_keywords(self, text: str) -> list:
        """
        Extract key technical terms from text.
        Simple implementation - can be enhanced with NLP.
        """
        # Common technical keywords
        tech_terms = [
            's3', 'sftp', 'api', 'database', 'lambda', 'ec2', 'rds',
            'kubernetes', 'docker', 'microservice', 'gateway', 'queue',
            'kafka', 'redis', 'postgresql', 'mongodb', 'rest', 'graphql'
        ]
        
        text_lower = text.lower()
        found_keywords = [term for term in tech_terms if term in text_lower]
        
        return found_keywords[:10]  # Limit to 10 keywords
    
    def _should_retrain(self, db: Session) -> bool:
        """
        Check if we have enough new feedback to trigger retraining.
        """
        # Count recent feedback items
        recent_count = db.query(ValidatedInput).filter(
            ValidatedInput.created_at >= datetime.utcnow().replace(hour=0, minute=0, second=0)
        ).count()
        
        return recent_count >= self.retraining_threshold
    
    def _trigger_retraining(self, db: Session):
        """
        Trigger model retraining (placeholder for future ML pipeline).
        In production, this would queue a background job.
        """
        # TODO: Implement actual retraining pipeline
        # For now, just log that retraining should happen
        print(f"[LEARNING] Retraining threshold reached. Queuing retraining job...")
        
        # In production:
        # - Queue background job (Celery, AWS Batch, etc.)
        # - Retrain classification model
        # - Update pattern recognition
        # - Rebuild vector index
        pass
    
    def get_learning_stats(self, db: Session) -> dict:
        """
        Get statistics about the learning system.
        """
        total_validated = db.query(ValidatedInput).count()
        valid_count = db.query(ValidatedInput).filter(
            ValidatedInput.user_feedback == 'valid'
        ).count()
        
        patterns_count = db.query(LearnedPattern).count()
        high_confidence_patterns = db.query(LearnedPattern).filter(
            LearnedPattern.confidence_score >= 0.8
        ).count()
        
        return {
            'total_validated_inputs': total_validated,
            'valid_inputs': valid_count,
            'learned_patterns': patterns_count,
            'high_confidence_patterns': high_confidence_patterns,
            'learning_rate': valid_count / total_validated if total_validated > 0 else 0
        }

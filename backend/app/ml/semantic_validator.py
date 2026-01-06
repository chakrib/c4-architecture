from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from typing import List, Tuple, Optional
from sqlalchemy.orm import Session
from app.models.database import ValidatedInput, LearnedPattern
from app.core.config import settings


class SemanticValidator:
    """
    ML-based semantic validation using sentence embeddings.
    Learns from validated examples to improve over time.
    """
    
    def __init__(self):
        self.model = SentenceTransformer(settings.EMBEDDING_MODEL)
        self.similarity_threshold = settings.SIMILARITY_THRESHOLD
        
    def encode_text(self, text: str) -> np.ndarray:
        """Generate embedding for input text"""
        return self.model.encode(text, convert_to_numpy=True)
    
    def find_similar_validated_inputs(
        self, 
        input_text: str, 
        db: Session,
        top_k: int = 5
    ) -> List[Tuple[ValidatedInput, float]]:
        """
        Find similar validated inputs using semantic search.
        Returns list of (ValidatedInput, similarity_score) tuples.
        """
        # Generate embedding for input
        input_embedding = self.encode_text(input_text)
        
        # Query validated inputs with embeddings
        validated_inputs = db.query(ValidatedInput).filter(
            ValidatedInput.embedding.isnot(None),
            ValidatedInput.user_feedback == 'valid'
        ).all()
        
        if not validated_inputs:
            return []
        
        # Calculate similarities
        similarities = []
        for validated in validated_inputs:
            if validated.embedding:
                # Convert pgvector to numpy array
                stored_embedding = np.array(validated.embedding)
                similarity = cosine_similarity(
                    input_embedding.reshape(1, -1),
                    stored_embedding.reshape(1, -1)
                )[0][0]
                similarities.append((validated, float(similarity)))
        
        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def validate_semantically(
        self, 
        input_text: str, 
        db: Session
    ) -> dict:
        """
        Validate input using semantic similarity to known valid examples.
        Returns validation result with confidence score.
        """
        similar_inputs = self.find_similar_validated_inputs(input_text, db)
        
        if not similar_inputs:
            return {
                'has_similar_examples': False,
                'confidence': 0.0,
                'similar_examples': []
            }
        
        # Get highest similarity score
        highest_similarity = similar_inputs[0][1]
        
        return {
            'has_similar_examples': True,
            'confidence': highest_similarity,
            'is_likely_valid': highest_similarity >= self.similarity_threshold,
            'similar_examples': [
                {
                    'text': inp.input_text[:100] + '...' if len(inp.input_text) > 100 else inp.input_text,
                    'similarity': score,
                    'pattern_type': inp.pattern_type
                }
                for inp, score in similar_inputs[:3]
            ]
        }
    
    def recognize_pattern(self, input_text: str, db: Session) -> Optional[str]:
        """
        Recognize architecture pattern from input text.
        Returns pattern name if recognized with high confidence.
        """
        patterns = db.query(LearnedPattern).filter(
            LearnedPattern.confidence_score >= 0.7
        ).all()
        
        input_lower = input_text.lower()
        
        for pattern in patterns:
            # Check keyword matches
            keyword_matches = sum(1 for kw in pattern.keywords if kw.lower() in input_lower)
            match_ratio = keyword_matches / len(pattern.keywords) if pattern.keywords else 0
            
            if match_ratio >= 0.5:  # At least 50% keywords match
                return pattern.pattern_name
        
        return None
    
    def suggest_pattern_components(
        self, 
        pattern_name: str, 
        db: Session
    ) -> List[str]:
        """
        Suggest typical components for a recognized pattern.
        """
        pattern = db.query(LearnedPattern).filter(
            LearnedPattern.pattern_name == pattern_name
        ).first()
        
        if not pattern:
            return []
        
        # Pattern-specific suggestions
        suggestions_map = {
            'file_transfer': [
                'Consider mentioning the source storage (e.g., S3, local filesystem)',
                'Specify the destination (e.g., SFTP server, database)',
                'Describe what triggers the transfer (event, schedule, manual)',
                'Mention any transformation or validation steps'
            ],
            'api_integration': [
                'Specify which systems expose APIs',
                'Describe the API protocol (REST, GraphQL, gRPC)',
                'Mention authentication method',
                'Describe what data is exchanged'
            ],
            'event_driven': [
                'Identify event sources (what generates events)',
                'Specify event consumers (what processes events)',
                'Mention the message broker (Kafka, SQS, EventBridge)',
                'Describe event types and their purposes'
            ],
            'microservices': [
                'List the main microservices',
                'Describe how services communicate',
                'Mention shared data stores if any',
                'Specify API gateway or service mesh'
            ],
            'data_pipeline': [
                'Identify data sources',
                'Describe transformation steps',
                'Specify data destinations',
                'Mention orchestration tool (Airflow, Step Functions)'
            ]
        }
        
        return suggestions_map.get(pattern_name, [])

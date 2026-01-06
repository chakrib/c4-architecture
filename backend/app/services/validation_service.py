from sqlalchemy.orm import Session
from app.models.schemas import ValidationResult
from app.ml.semantic_validator import SemanticValidator
from app.ml.gap_analyzer import GapAnalyzer
from typing import List, Dict


class ValidationService:
    """
    Comprehensive validation service combining rule-based and ML-based validation.
    """
    
    def __init__(self):
        self.semantic_validator = SemanticValidator()
        self.gap_analyzer = GapAnalyzer()
        
        # Rule-based validation keywords
        self.system_keywords = ['system', 'application', 'service', 'platform', 'api', 'database']
        self.user_keywords = ['user', 'customer', 'admin', 'operator', 'developer']
        self.container_keywords = ['web', 'mobile', 'api', 'database', 'cache', 'lambda', 's3', 'server']
        self.relationship_keywords = ['connect', 'send', 'receive', 'call', 'transfer', 'integrate']
        
        # Entertainment/non-technical keywords to block
        self.blocked_keywords = [
            'movie', 'film', 'show', 'series', 'episode', 'actor', 'actress',
            'director', 'cinema', 'theater', 'plot', 'character', 'scene'
        ]
    
    async def validate_with_learning(
        self,
        input_text: str,
        user_id: int,
        db: Session
    ) -> ValidationResult:
        """
        Validate input using both rule-based and ML-based approaches.
        """
        errors = []
        warnings = []
        suggestions = []
        
        # Step 1: Basic validation
        if not input_text or len(input_text.strip()) < 15:
            errors.append({
                'category': 'Input Length',
                'message': 'Input too short. Please provide at least 15 words.',
                'severity': 'error'
            })
            return ValidationResult(
                is_valid=False,
                score=0.0,
                errors=errors,
                warnings=warnings,
                suggestions=suggestions
            )
        
        text_lower = input_text.lower()
        
        # Step 2: Block non-technical content
        blocked_found = [kw for kw in self.blocked_keywords if kw in text_lower]
        if blocked_found:
            errors.append({
                'category': 'Content Type',
                'message': f'This appears to be non-technical content (found: {", ".join(blocked_found)})',
                'severity': 'error'
            })
            return ValidationResult(
                is_valid=False,
                score=0.0,
                errors=errors,
                warnings=warnings,
                suggestions=['Please provide a technical solution overview, not entertainment content.']
            )
        
        # Step 3: Rule-based validation
        has_systems = any(kw in text_lower for kw in self.system_keywords)
        has_users = any(kw in text_lower for kw in self.user_keywords)
        has_containers = any(kw in text_lower for kw in self.container_keywords)
        has_relationships = any(kw in text_lower for kw in self.relationship_keywords)
        
        # Check for specific services (more lenient)
        has_specific_services = bool(re.search(
            r's3|sftp|lambda|ec2|rds|whatsapp|google docs|dashboard|api|database',
            text_lower
        ))
        
        if not has_systems and not has_specific_services:
            errors.append({
                'category': 'System Context',
                'message': 'No clear system or service identified',
                'severity': 'error'
            })
        
        if not has_containers and not has_specific_services:
            errors.append({
                'category': 'Components',
                'message': 'No technical components identified',
                'severity': 'error'
            })
        
        if not has_users:
            warnings.append({
                'category': 'Actors',
                'message': 'No users or actors mentioned',
                'severity': 'warning'
            })
        
        if not has_relationships:
            warnings.append({
                'category': 'Relationships',
                'message': 'No interactions or data flows described',
                'severity': 'warning'
            })
        
        # Step 4: Semantic validation (ML-based)
        semantic_result = self.semantic_validator.validate_semantically(input_text, db)
        
        if semantic_result['has_similar_examples']:
            if semantic_result['is_likely_valid']:
                suggestions.append(
                    f"✓ Similar to validated examples (confidence: {semantic_result['confidence']:.0%})"
                )
            else:
                warnings.append({
                    'category': 'Semantic Similarity',
                    'message': f"Somewhat similar to known patterns but below threshold (confidence: {semantic_result['confidence']:.0%})",
                    'severity': 'info'
                })
        
        # Step 5: Pattern recognition
        recognized_pattern = self.semantic_validator.recognize_pattern(input_text, db)
        if recognized_pattern:
            pattern_suggestions = self.semantic_validator.suggest_pattern_components(
                recognized_pattern, db
            )
            suggestions.extend(pattern_suggestions[:3])  # Add top 3 suggestions
        
        # Step 6: Gap analysis
        gap_analysis = self.gap_analyzer.analyze(
            input_text,
            errors,
            semantic_result.get('similar_examples', [])
        )
        
        # Add gap analysis suggestions
        suggestions.extend(gap_analysis.suggestions[:5])
        
        # Step 7: Calculate score
        score = self._calculate_score(
            has_systems or has_specific_services,
            has_users,
            has_containers or has_specific_services,
            has_relationships,
            semantic_result.get('confidence', 0.0),
            len(errors),
            len(warnings)
        )
        
        # Determine if valid
        is_valid = len(errors) == 0 and score >= 50.0
        
        return ValidationResult(
            is_valid=is_valid,
            score=score,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            gap_analysis=gap_analysis.dict() if gap_analysis else None
        )
    
    def _calculate_score(
        self,
        has_systems: bool,
        has_users: bool,
        has_containers: bool,
        has_relationships: bool,
        semantic_confidence: float,
        error_count: int,
        warning_count: int
    ) -> float:
        """
        Calculate validation score (0-100).
        """
        score = 100.0
        
        # Deduct for missing elements
        if not has_systems:
            score -= 30
        if not has_containers:
            score -= 25
        if not has_users:
            score -= 10
        if not has_relationships:
            score -= 10
        
        # Deduct for errors and warnings
        score -= error_count * 20
        score -= warning_count * 5
        
        # Boost for semantic similarity
        score += semantic_confidence * 15
        
        return max(0.0, min(100.0, score))


import re  # Add at top of file

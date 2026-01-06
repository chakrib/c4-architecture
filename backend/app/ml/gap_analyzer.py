from typing import List, Dict
import re
from app.models.schemas import GapAnalysis, SimilarPattern


class GapAnalyzer:
    """
    Analyzes solution overviews to identify missing information
    and provide intelligent, actionable guidance.
    """
    
    def __init__(self):
        self.component_keywords = [
            'system', 'application', 'service', 'platform', 'api',
            'database', 'storage', 's3', 'server', 'lambda', 'function'
        ]
        
        self.actor_keywords = [
            'user', 'customer', 'admin', 'operator', 'developer',
            'manager', 'employee', 'client', 'actor'
        ]
        
        self.relationship_keywords = [
            'connect', 'communicate', 'send', 'receive', 'call',
            'request', 'response', 'transfer', 'integrate', 'access',
            'trigger', 'process', 'store', 'retrieve'
        ]
    
    def analyze(
        self, 
        input_text: str, 
        validation_errors: List[dict],
        similar_patterns: List[dict] = None
    ) -> GapAnalysis:
        """
        Perform comprehensive gap analysis and generate actionable suggestions.
        """
        text_lower = input_text.lower()
        
        # Detect what's present
        has_components = any(kw in text_lower for kw in self.component_keywords)
        has_actors = any(kw in text_lower for kw in self.actor_keywords)
        has_relationships = any(kw in text_lower for kw in self.relationship_keywords)
        
        # Identify specific gaps
        missing_components = []
        missing_actors = []
        missing_relationships = []
        ambiguous_terms = []
        suggestions = []
        
        # Analyze components
        if not has_components:
            missing_components.append('No technical components identified')
            suggestions.append(
                "🔷 Add technical components: Mention specific systems, services, or applications. "
                "Example: 'The system uses an API Gateway, Lambda functions, and DynamoDB.'"
            )
        else:
            # Check for specific component types
            if 'database' not in text_lower and 'storage' not in text_lower:
                suggestions.append(
                    "💾 Consider data storage: Where is data stored? "
                    "(e.g., 'Data is stored in PostgreSQL' or 'Files are kept in S3')"
                )
        
        # Analyze actors
        if not has_actors:
            missing_actors.append('No users or actors mentioned')
            suggestions.append(
                "👤 Specify who uses the system: Who interacts with it? "
                "Example: 'Customers use the mobile app' or 'Administrators manage via dashboard'"
            )
        
        # Analyze relationships
        if not has_relationships:
            missing_relationships.append('No interactions or data flows described')
            suggestions.append(
                "🔄 Describe interactions: How do components work together? "
                "Example: 'The API receives requests from the frontend and queries the database'"
            )
        
        # Check for ambiguous terms
        ambiguous_patterns = [
            (r'\bsystem\b', 'system', 'Which specific system? Give it a name or describe its purpose.'),
            (r'\bapplication\b', 'application', 'Which application? Specify its name or function.'),
            (r'\bdata\b', 'data', 'What kind of data? (e.g., user profiles, transaction records, files)'),
            (r'\bprocess\b', 'process', 'What process? Describe what happens step by step.')
        ]
        
        for pattern, term, suggestion in ambiguous_patterns:
            if re.search(pattern, text_lower):
                ambiguous_terms.append(term)
                if len(suggestions) < 8:  # Limit suggestions
                    suggestions.append(f"❓ Clarify '{term}': {suggestion}")
        
        # Add context-specific suggestions based on detected patterns
        if 'whatsapp' in text_lower or 'google docs' in text_lower:
            suggestions.append(
                "📱 Integration details: How do you connect to WhatsApp/Google Docs? "
                "(API, webhook, polling?)"
            )
        
        if 'dashboard' in text_lower:
            suggestions.append(
                "📊 Dashboard specifics: What data does it display? Who accesses it? "
                "What actions can users take?"
            )
        
        # Convert similar patterns to schema
        similar_pattern_objects = []
        if similar_patterns:
            for pattern in similar_patterns[:3]:
                similar_pattern_objects.append(
                    SimilarPattern(
                        pattern_name=pattern.get('pattern_type', 'Unknown'),
                        similarity_score=pattern.get('similarity', 0.0),
                        example_input=pattern.get('text', '')
                    )
                )
        
        return GapAnalysis(
            missing_components=missing_components,
            missing_actors=missing_actors,
            missing_relationships=missing_relationships,
            ambiguous_terms=ambiguous_terms,
            suggestions=suggestions[:10],  # Limit to top 10 suggestions
            similar_patterns=similar_pattern_objects
        )
    
    def generate_improvement_prompt(self, gap_analysis: GapAnalysis) -> str:
        """
        Generate a user-friendly prompt to help improve their input.
        """
        prompt_parts = ["To generate a better diagram, consider adding:\n"]
        
        if gap_analysis.missing_components:
            prompt_parts.append("\n🔷 Technical Components:")
            for suggestion in gap_analysis.suggestions:
                if '🔷' in suggestion:
                    prompt_parts.append(f"  • {suggestion.replace('🔷 ', '')}")
        
        if gap_analysis.missing_actors:
            prompt_parts.append("\n👤 Users/Actors:")
            for suggestion in gap_analysis.suggestions:
                if '👤' in suggestion:
                    prompt_parts.append(f"  • {suggestion.replace('👤 ', '')}")
        
        if gap_analysis.missing_relationships:
            prompt_parts.append("\n🔄 Interactions:")
            for suggestion in gap_analysis.suggestions:
                if '🔄' in suggestion:
                    prompt_parts.append(f"  • {suggestion.replace('🔄 ', '')}")
        
        if gap_analysis.similar_patterns:
            prompt_parts.append("\n💡 Similar patterns found:")
            for pattern in gap_analysis.similar_patterns:
                prompt_parts.append(
                    f"  • {pattern.pattern_name} "
                    f"({pattern.similarity_score:.0%} match)"
                )
        
        return "\n".join(prompt_parts)

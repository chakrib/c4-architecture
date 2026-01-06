from anthropic import Anthropic
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.database import Diagram, UsageLog
from app.models.schemas import DiagramGenerateRequest, DiagramGenerateResponse, ValidationResult
from app.services.validation_service import ValidationService
from typing import Optional


class DiagramService:
    """
    Service for generating C4 diagrams using Claude AI.
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.validation_service = ValidationService()
    
    async def generate_diagram(
        self,
        request: DiagramGenerateRequest,
        user_id: int,
        db: Session
    ) -> DiagramGenerateResponse:
        """
        Generate a C4 diagram from solution overview text.
        """
        # Step 1: Validate input
        validation = await self.validation_service.validate_with_learning(
            request.input_text,
            user_id,
            db
        )
        
        if not validation.is_valid:
            # Return validation errors without generating
            return DiagramGenerateResponse(
                diagram_id=None,
                mermaid_code='',
                validation=validation,
                metadata={'generated': False, 'reason': 'validation_failed'}
            )
        
        # Step 2: Build intelligent prompt
        prompt = self._build_prompt(request.input_text, request.diagram_type)
        
        # Step 3: Generate diagram with Claude
        try:
            mermaid_code = await self._generate_with_claude(prompt)
            
            # Step 4: Sanitize generated code
            mermaid_code = self._sanitize_mermaid_code(mermaid_code)
            
            # Step 5: Save diagram if requested
            diagram_id = None
            if request.save_diagram:
                diagram = Diagram(
                    title=request.title or f"Diagram - {request.diagram_type}",
                    description=request.input_text[:500],
                    input_text=request.input_text,
                    mermaid_code=mermaid_code,
                    diagram_type=request.diagram_type,
                    user_id=user_id
                )
                db.add(diagram)
                db.commit()
                db.refresh(diagram)
                diagram_id = diagram.id
            
            # Step 6: Log usage
            self._log_usage(
                user_id=user_id,
                action='generate',
                input_length=len(request.input_text),
                success=True,
                db=db
            )
            
            return DiagramGenerateResponse(
                diagram_id=diagram_id,
                mermaid_code=mermaid_code,
                validation=validation,
                metadata={
                    'generated': True,
                    'diagram_type': request.diagram_type,
                    'model': 'claude-3-haiku-20240307'
                }
            )
            
        except Exception as e:
            # Log failure
            self._log_usage(
                user_id=user_id,
                action='generate',
                input_length=len(request.input_text),
                success=False,
                error_message=str(e),
                db=db
            )
            raise
    
    def _build_prompt(self, context: str, diagram_type: str) -> str:
        """
        Build intelligent prompt for Claude based on context analysis.
        """
        base_prompt = f"""You are an expert software architect. Generate a clear, legible {diagram_type} diagram using Mermaid flowchart syntax.

Solution Context:
{context}

CRITICAL SYNTAX RULES:
1. Use standard Mermaid flowchart syntax: "graph LR" (Left-to-Right) or "graph TD" (Top-Down)
2. Node IDs MUST be simple alphanumeric (no spaces, no special chars): UserNode, S3Bucket, TransferSys
3. NEVER use reserved words as node IDs: "system", "application", "graph", "class", "end"
4. If you need to use a reserved word, prefix it: node_system, node_application
5. Labels go inside brackets: UserNode[👤 User<br/>Description]

TEMPLATE:
```
graph LR
    UserNode[👤 User<br/>Description]
    MainSys[🔷 System Name<br/>Description]
    ExternalSvc[📦 External System<br/>Description]
    
    UserNode -->|Action| MainSys
    MainSys -->|Action| ExternalSvc
    
    classDef userStyle fill:#08427B,stroke:#052E56,color:#fff
    classDef systemStyle fill:#1168BD,stroke:#0B4884,color:#fff
    classDef externalStyle fill:#999,stroke:#666,color:#fff
    
    class UserNode userStyle
    class MainSys systemStyle
    class ExternalSvc externalStyle
```

RULES:
- Use "graph LR" for simple flows (≤5 elements)
- Use "graph TD" for complex hierarchies (>5 elements)
- Keep labels SHORT (max 3-4 words per line)
- Use <br/> for line breaks
- Add icons: 👤 users, 🔷 systems, 📦 external, 💾 databases
- Clear relationship labels on arrows

Generate ONLY the Mermaid code without markdown blocks."""
        
        return base_prompt
    
    async def _generate_with_claude(self, prompt: str) -> str:
        """
        Call Claude API to generate diagram.
        """
        message = self.client.messages.create(
            model='claude-3-haiku-20240307',
            max_tokens=2000,
            messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        )
        
        mermaid_code = message.content[0].text.strip()
        
        # Clean up markdown blocks if present
        mermaid_code = mermaid_code.replace('```mermaid\n', '')
        mermaid_code = mermaid_code.replace('```mermaid', '')
        mermaid_code = mermaid_code.replace('```\n', '')
        mermaid_code = mermaid_code.replace('```', '')
        
        return mermaid_code.strip()
    
    def _sanitize_mermaid_code(self, code: str) -> str:
        """
        Sanitize generated Mermaid code to fix common issues.
        """
        reserved_words = ['graph', 'subgraph', 'end', 'class', 'classDef', 'click', 'style', 'system', 'application']
        
        lines = code.split('\n')
        sanitized_lines = []
        node_id_map = {}
        
        for line in lines:
            sanitized_line = line
            
            # Fix node IDs that are reserved words
            for word in reserved_words:
                if f'{word}[' in sanitized_line.lower() or f'{word}(' in sanitized_line.lower():
                    sanitized_line = sanitized_line.replace(f'{word}[', f'node_{word}[')
                    sanitized_line = sanitized_line.replace(f'{word}(', f'node_{word}(')
                    node_id_map[word] = f'node_{word}'
            
            sanitized_lines.append(sanitized_line)
        
        return '\n'.join(sanitized_lines)
    
    def _log_usage(
        self,
        user_id: int,
        action: str,
        input_length: int,
        success: bool,
        error_message: Optional[str] = None,
        db: Session = None
    ):
        """
        Log API usage for analytics and cost tracking.
        """
        if not db:
            return
        
        # Estimate tokens (rough approximation)
        tokens_used = input_length // 4 if success else 0
        
        # Estimate cost (Claude Haiku pricing: ~$0.25 per 1M input tokens)
        cost_estimate = (tokens_used / 1_000_000) * 0.25
        
        usage_log = UsageLog(
            user_id=user_id,
            action=action,
            input_length=input_length,
            tokens_used=tokens_used,
            cost_estimate=cost_estimate,
            success=success,
            error_message=error_message
        )
        
        db.add(usage_log)
        db.commit()

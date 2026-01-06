from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import anthropic
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Simple mode - no database/Redis for now
USE_DATABASE = os.getenv("USE_DATABASE", "false").lower() == "true"

app = FastAPI(
    title="C4 Diagram Generator API",
    version="1.0.0",
    description="C4 diagram generation with intelligent validation"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DiagramRequest(BaseModel):
    input_text: str
    diagram_type: str = "context"


class ValidationResult(BaseModel):
    is_valid: bool
    errors: list[str]
    warnings: list[str]
    suggestions: list[str]
    questions: list[str] = []  # Questions to ask user for clarification


class SuggestionOption(BaseModel):
    title: str
    description: str
    improved_text: str


class SuggestionResponse(BaseModel):
    original_text: str
    validation_issues: list[str]
    suggestions: list[SuggestionOption]


class RefinementRequest(BaseModel):
    current_mermaid: str
    original_context: str
    refinement_instruction: str


class RefinementResponse(BaseModel):
    updated_mermaid: str
    changes_made: list[str]
    explanation: str


class DiagramResponse(BaseModel):
    mermaid_code: str
    validation: ValidationResult


def validate_input(text: str) -> ValidationResult:
    """
    Validate input for C4 diagram generation.
    Focus on identifying minimum requirements for C4 Level 1.
    
    C4 Level 1 (Context Diagram) requires:
    1. The System being built (mandatory)
    2. Users/Actors who interact with it (mandatory)
    3. External systems it integrates with (optional but helpful)
    """
    errors = []
    warnings = []
    suggestions = []
    questions = []
    
    # Check for empty input
    if not text or not text.strip():
        errors.append("Empty input provided")
        suggestions.append("Please describe the system you want to build")
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings, suggestions=suggestions, questions=questions)
    
    # Check minimum word count (15 words)
    words = text.split()
    word_count = len(words)
    
    if word_count < 15:
        errors.append(f"Input too short ({word_count} words). Need at least 15 words for meaningful C4 diagram.")
        suggestions.append("Please provide more details about:")
        suggestions.append("  • What system/application are you building?")
        suggestions.append("  • Who will use it?")
        suggestions.append("  • What does it do?")
        suggestions.append("  • What external systems does it connect to?")
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings, suggestions=suggestions, questions=questions)
    
    text_lower = text.lower()
    
    # Check for gibberish - look for meaningful words
    # If text has very few recognizable technical/business terms, it's likely gibberish
    meaningful_words = [
        # Actions
        'build', 'create', 'develop', 'make', 'design', 'implement', 'deploy',
        # Systems
        'system', 'application', 'app', 'service', 'platform', 'tool', 'software',
        'web', 'mobile', 'api', 'backend', 'frontend', 'dashboard', 'website', 'portal', 'interface',
        # Users
        'user', 'users', 'customer', 'customers', 'admin', 'administrator', 'client', 'clients',
        'people', 'person', 'employee', 'staff', 'developer', 'manager', 'operator', 'visitor', 'member',
        # Common tech terms
        'data', 'database', 'server', 'cloud', 'storage', 'file', 'files', 'upload', 'download',
        'authentication', 'authorization', 'payment', 'order', 'process', 'manage', 'track',
        'send', 'receive', 'store', 'retrieve', 'display', 'show', 'view', 'edit', 'delete',
        # Business terms
        'business', 'company', 'organization', 'team', 'department', 'workflow', 'process',
        'report', 'analytics', 'dashboard', 'notification', 'alert', 'message', 'email',
        # Integration terms
        'integrate', 'connect', 'sync', 'transfer', 'import', 'export', 'api', 'webhook'
    ]
    
    meaningful_count = sum(1 for word in meaningful_words if word in text_lower)
    
    # If less than 3 meaningful words in 15+ words, likely gibberish
    if meaningful_count < 3:
        errors.append("Input appears to be gibberish or lacks technical/business context")
        suggestions.append("Please describe a real system or application using clear language")
        suggestions.append("Example: 'Build a web application where users can upload documents, store them in cloud storage, and share them with team members'")
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings, suggestions=suggestions, questions=questions)
    
    # C4 Level 1 Requirements Check
    
    # 1. Check for THE SYSTEM (what are we building?)
    system_indicators = [
        'build', 'create', 'develop', 'make', 'design', 'implement',
        'system', 'application', 'app', 'service', 'platform', 'tool', 'software',
        'web', 'mobile', 'api', 'backend', 'frontend', 'dashboard',
        'website', 'portal', 'interface'
    ]
    
    has_system = any(indicator in text_lower for indicator in system_indicators)
    
    if not has_system:
        errors.append("Cannot identify what system/application you want to build")
        questions.append("What type of system are you building? (e.g., web app, mobile app, API service, platform)")
        suggestions.append("Please specify the system you want to create")
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings, suggestions=suggestions, questions=questions)
    
    # 2. Check for USERS/ACTORS (who uses it?)
    user_indicators = [
        'user', 'users', 'customer', 'customers', 'admin', 'administrator',
        'client', 'clients', 'people', 'person', 'employee', 'staff',
        'developer', 'manager', 'operator', 'visitor', 'member', 'team'
    ]
    
    has_users = any(indicator in text_lower for indicator in user_indicators)
    
    if not has_users:
        # This is critical for C4 Level 1 - ask a question
        questions.append("Who will use this system? (e.g., customers, employees, administrators)")
        warnings.append("C4 Context diagrams require identifying the users/actors")
        suggestions.append("Add information about who will interact with the system")
    
    # 3. Check for FUNCTIONALITY (what does it do?)
    functionality_indicators = [
        'upload', 'download', 'store', 'retrieve', 'process', 'manage', 'track',
        'send', 'receive', 'display', 'show', 'view', 'edit', 'delete', 'create',
        'update', 'search', 'filter', 'sort', 'analyze', 'report', 'notify',
        'authenticate', 'authorize', 'pay', 'order', 'book', 'schedule', 'share',
        # Dashboard and analytics verbs
        'determine', 'identify', 'monitor', 'visualize', 'review', 'assess', 'evaluate',
        'compare', 'measure', 'calculate', 'aggregate', 'summarize', 'forecast',
        'predict', 'detect', 'discover', 'explore', 'inspect', 'examine',
        # Data interaction verbs
        'generate', 'produce', 'compile', 'collect', 'gather', 'extract', 'transform',
        'load', 'import', 'export', 'sync', 'integrate', 'consolidate',
        # User actions
        'access', 'browse', 'navigate', 'select', 'choose', 'configure', 'customize',
        'submit', 'approve', 'reject', 'request', 'respond', 'comment', 'collaborate'
    ]
    
    has_functionality = any(indicator in text_lower for indicator in functionality_indicators)
    
    if not has_functionality:
        questions.append("What will users do with this system? What are the main features?")
        warnings.append("No clear functionality described")
        suggestions.append("Describe what users can do with the system")
    
    # 4. Check for EXTERNAL SYSTEMS (optional but helpful)
    external_indicators = [
        'integrate', 'connect', 'sync', 'api', 'database', 'storage', 's3', 'aws',
        'google', 'microsoft', 'salesforce', 'stripe', 'paypal', 'twilio',
        'slack', 'email', 'sms', 'webhook', 'third-party', 'external',
        # Specific services
        'whatsapp', 'gmail', 'docs', 'sheets', 'drive', 'dropbox', 'box',
        'azure', 'gcp', 'firebase', 'supabase', 'mongodb', 'postgresql', 'mysql',
        'redis', 'elasticsearch', 'kafka', 'rabbitmq', 'sendgrid', 'mailchimp',
        'zendesk', 'jira', 'confluence', 'github', 'gitlab', 'bitbucket',
        'shopify', 'woocommerce', 'magento', 'wordpress', 'hubspot'
    ]
    
    has_external = any(indicator in text_lower for indicator in external_indicators)
    
    if not has_external:
        warnings.append("No external systems or integrations mentioned")
        suggestions.append("Consider mentioning: databases, cloud storage, third-party APIs, or external services")
    
    # If we have critical questions, mark as invalid and ask for clarification
    if questions:
        errors.append("Insufficient information for C4 Context diagram")
        return ValidationResult(is_valid=False, errors=errors, warnings=warnings, suggestions=suggestions, questions=questions)
    
    # If we only have warnings but no questions, it's valid but could be better
    return ValidationResult(is_valid=True, errors=errors, warnings=warnings, suggestions=suggestions, questions=questions)


def generate_improvement_suggestions(original_text: str, validation_result: ValidationResult) -> list[SuggestionOption]:
    """
    Use Claude to generate improved versions of the input text that would pass validation.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return []
    
    # Build a prompt for Claude to generate suggestions
    prompt = f"""You are an expert at translating business/technical descriptions into C4 Context diagram requirements.

A user provided this description:
"{original_text}"

This description has validation issues:
{', '.join(validation_result.errors + validation_result.questions)}

For C4 Level 1 (Context) diagrams, we need:
1. THE SYSTEM being built (what software/service)
2. USERS/ACTORS (who uses it)
3. FUNCTIONALITY (what does it do)
4. EXTERNAL SYSTEMS (what does it integrate with)

Based on the user's description, generate 3 different interpretations that would be suitable for C4 diagrams. Each should be a complete, clear description (50-100 words) that includes all 4 required elements.

Format your response as JSON:
{{
  "suggestions": [
    {{
      "title": "Brief title (5-7 words)",
      "description": "One sentence explaining this interpretation",
      "improved_text": "Complete description with system, users, functionality, and external systems"
    }},
    ... (2 more suggestions)
  ]
}}

Make the suggestions diverse - consider different angles like:
- Enforcement/prevention system
- Monitoring/auditing tool
- Automation/provisioning service
- Governance/compliance platform

Return ONLY the JSON, no other text."""

    try:
        client = anthropic.Anthropic(api_key=api_key, http_client=None)
        
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text.strip()
        
        # Parse JSON response
        import json
        response_data = json.loads(response_text)
        
        suggestions = []
        for item in response_data.get("suggestions", []):
            suggestions.append(SuggestionOption(
                title=item["title"],
                description=item["description"],
                improved_text=item["improved_text"]
            ))
        
        return suggestions
        
    except Exception as e:
        print(f"Error generating suggestions: {str(e)}")
        return []


def refine_diagram(current_mermaid: str, original_context: str, refinement_instruction: str) -> dict:
    """
    Use Claude to refine an existing Mermaid diagram based on user instructions.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise Exception("Anthropic API key not configured")
    
    prompt = f"""You are an expert at modifying Mermaid C4 diagrams based on user instructions.

CURRENT DIAGRAM:
```
{current_mermaid}
```

ORIGINAL CONTEXT:
{original_context}

USER'S REFINEMENT REQUEST:
"{refinement_instruction}"

Your task:
1. Understand what the user wants to change
2. Modify the Mermaid diagram accordingly
3. Maintain proper Mermaid syntax
4. Keep the diagram clean and legible

CRITICAL RULES:
- Use standard Mermaid flowchart syntax (graph LR or graph TD)
- Node IDs must be alphanumeric (no spaces, no special chars)
- NEVER use reserved words as node IDs: "system", "application", "graph", "class", "end"
- Keep labels SHORT and clear
- Maintain consistent styling with classDef
- Use icons: 👤 for users, 🔷 for systems, 📦 for external systems, 💾 for databases

Common modifications:
- REMOVE: Delete specified nodes and their connections
- ADD: Insert new nodes with appropriate connections
- EDIT LABEL: Change the text inside brackets [...]
- REPOSITION: Adjust node order (left/right in LR, top/bottom in TD)
- SIMPLIFY: Remove unnecessary details or nodes
- ENHANCE: Add more detail or connections

Format your response as JSON:
{{
  "updated_mermaid": "Complete updated Mermaid code",
  "changes_made": ["List of changes", "Another change"],
  "explanation": "Brief explanation of what was modified and why"
}}

Return ONLY the JSON, no markdown code blocks."""

    try:
        client = anthropic.Anthropic(api_key=api_key, http_client=None)
        
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        
        response_text = message.content[0].text.strip()
        
        # Parse JSON response
        import json
        response_data = json.loads(response_text)
        
        return response_data
        
    except Exception as e:
        print(f"Error refining diagram: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise Exception(f"Failed to refine diagram: {str(e)}")


def build_prompt(context: str) -> str:
    """Build the prompt for Claude to generate C4 diagram."""
    return f"""You are an expert software architect. Based on the following solution context, generate a clear, legible architecture diagram using Mermaid flowchart syntax (NOT C4Context).

Solution Context:
{context}

CRITICAL SYNTAX RULES:
1. Use standard Mermaid flowchart syntax with LEFT-TO-RIGHT (LR) direction
2. Node IDs MUST be simple alphanumeric (no spaces, no special chars): User, S3Bucket, TransferSystem
3. NEVER use reserved words as node IDs: "system", "application", "graph", "class", "end"
4. If you need to use a reserved word, prefix it: node_system, node_application
5. Labels go inside brackets and can have any text: User[👤 User<br/>Uploads files]

CORRECT SYNTAX EXAMPLES:
✓ User[👤 User]
✓ S3Bucket[📦 Amazon S3]
✓ TransferSys[🔷 Transfer System]
✓ SFTPServer[📦 SFTP Server]

TEMPLATE TO FOLLOW:
```
graph LR
    %% Define nodes with clear IDs and styled labels
    UserNode[👤 User<br/>Description]
    MainSystem[🔷 System Name<br/>Description]
    ExternalSvc[📦 External System<br/>Description]
    
    %% Define relationships with clear labels
    UserNode -->|Action description| MainSystem
    MainSystem -->|Action description| ExternalSvc
    
    %% Apply styling
    classDef userStyle fill:#08427B,stroke:#052E56,color:#fff
    classDef systemStyle fill:#1168BD,stroke:#0B4884,color:#fff
    classDef externalStyle fill:#999,stroke:#666,color:#fff
    
    class UserNode userStyle
    class MainSystem systemStyle
    class ExternalSvc externalStyle
```

RULES FOR LEGIBLE DIAGRAMS:
1. ALWAYS use "graph LR" (Left-to-Right) for simple diagrams (≤5 elements)
2. Use "graph TD" (Top-Down) only for complex hierarchies (>5 elements)
3. Keep labels SHORT (max 3-4 words per line)
4. Use <br/> to break long text into multiple lines
5. Add icons: 👤 for users, 🔷 for systems, 📦 for external systems, 💾 for databases
6. Use clear, descriptive relationship labels on arrows
7. Apply consistent styling with classDef

STYLING GUIDE:
- Users/Actors: Dark blue (#08427B)
- Main Systems: Blue (#1168BD)
- External Systems: Gray (#999)
- Databases/Storage: Green (#2E7D32)

Generate a clean, horizontal, legible diagram following these rules. Return ONLY the Mermaid code without markdown code blocks."""


@app.get("/")
async def root():
    return {
        "message": "C4 Diagram Generator API",
        "version": "1.0.0",
        "status": "running",
        "database_enabled": USE_DATABASE
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/api/diagrams/suggest-improvements", response_model=SuggestionResponse)
async def suggest_improvements(request: DiagramRequest):
    """
    Analyze input and suggest improved versions that would pass validation.
    This is called when validation fails but the input isn't complete gibberish.
    """
    # Validate input
    validation = validate_input(request.input_text)
    
    # If it's valid, no need for suggestions
    if validation.is_valid:
        raise HTTPException(
            status_code=400,
            detail="Input is already valid. Use /api/diagrams/generate instead."
        )
    
    # If it's gibberish or too short, don't generate suggestions
    if any("gibberish" in error.lower() or "too short" in error.lower() for error in validation.errors):
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Cannot generate suggestions for this input",
                "errors": validation.errors,
                "suggestions": validation.suggestions
            }
        )
    
    # Generate improvement suggestions using Claude
    suggestions = generate_improvement_suggestions(request.input_text, validation)
    
    if not suggestions:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate suggestions. Please try rephrasing your input."
        )
    
    return SuggestionResponse(
        original_text=request.input_text,
        validation_issues=validation.errors + validation.questions,
        suggestions=suggestions
    )


@app.post("/api/diagrams/refine", response_model=RefinementResponse)
async def refine_diagram_endpoint(request: RefinementRequest):
    """
    Refine an existing diagram based on user instructions.
    Supports operations like: remove, add, edit labels, reposition, simplify, enhance.
    """
    try:
        result = refine_diagram(
            request.current_mermaid,
            request.original_context,
            request.refinement_instruction
        )
        
        return RefinementResponse(
            updated_mermaid=result["updated_mermaid"],
            changes_made=result["changes_made"],
            explanation=result["explanation"]
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refine diagram: {str(e)}"
        )


@app.post("/api/diagrams/generate", response_model=DiagramResponse)
async def generate_diagram(request: DiagramRequest):
    """Generate C4 diagram from input text."""
    
    # Validate input
    validation = validate_input(request.input_text)
    
    if not validation.is_valid:
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Validation failed",
                "errors": validation.errors,
                "suggestions": validation.suggestions,
                "questions": validation.questions
            }
        )
    
    # Get Anthropic API key from environment
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="Anthropic API key not configured")
    
    # Generate diagram using Claude
    try:
        # Create client without proxy settings
        client = anthropic.Anthropic(
            api_key=api_key,
            http_client=None  # Don't use custom http client
        )
        prompt = build_prompt(request.input_text)
        
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        mermaid_code = message.content[0].text.strip()
        
        # Clean up the response - remove markdown code blocks if present
        mermaid_code = mermaid_code.replace("```mermaid\n", "")
        mermaid_code = mermaid_code.replace("```mermaid", "")
        mermaid_code = mermaid_code.replace("```\n", "")
        mermaid_code = mermaid_code.replace("```", "")
        mermaid_code = mermaid_code.strip()
        
        return DiagramResponse(
            mermaid_code=mermaid_code,
            validation=validation
        )
        
    except Exception as e:
        import traceback
        print(f"Error generating diagram: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Failed to generate diagram: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

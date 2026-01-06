"""
Django Ninja API endpoints for C4 diagram generation.
"""
from ninja import NinjaAPI
from ninja.errors import HttpError
from .schemas import (
    DiagramRequest,
    DiagramResponse,
    SuggestionResponse,
    RefinementRequest,
    RefinementResponse,
    HealthResponse,
    ValidationResult
)
from .validation import validate_input
from .ai_service import generate_diagram, generate_improvement_suggestions, refine_diagram

# Create API instance
api = NinjaAPI(
    title="C4 Diagram Generator API",
    version="1.0.0",
    description="C4 diagram generation with intelligent validation using Django Ninja"
)


@api.get("/", response=HealthResponse)
def root(request):
    """API root endpoint."""
    return {
        "status": "running",
        "version": "1.0.0"
    }


@api.get("/health", response=HealthResponse)
def health_check(request):
    """Health check endpoint."""
    return {"status": "healthy"}


@api.post("/diagrams/validate", response=ValidationResult)
def validate_diagram_input(request, payload: DiagramRequest):
    """Validate input text for C4 diagram generation."""
    validation = validate_input(payload.input_text)
    return validation


@api.post("/diagrams/generate", response=DiagramResponse)
def generate_diagram_endpoint(request, payload: DiagramRequest):
    """Generate C4 diagram from input text."""
    
    # Validate input
    validation = validate_input(payload.input_text)
    
    if not validation.is_valid:
        from ninja.responses import Response
        # Return structured error with all validation details
        error_response = {
            "errors": validation.errors,
            "suggestions": validation.suggestions,
            "questions": validation.questions,
            "warnings": validation.warnings
        }
        return Response(error_response, status=400)
    
    # Generate diagram using Claude
    try:
        mermaid_code = generate_diagram(payload.input_text)
        
        return DiagramResponse(
            mermaid_code=mermaid_code,
            validation=validation
        )
        
    except Exception as e:
        from ninja.responses import Response
        return Response(
            {"message": f"Failed to generate diagram: {str(e)}"},
            status=500
        )


@api.post("/diagrams/suggest-improvements", response=SuggestionResponse)
def suggest_improvements(request, payload: DiagramRequest):
    """
    Analyze input and suggest improved versions that would pass validation.
    This is called when validation fails but the input isn't complete gibberish.
    """
    from ninja.responses import Response
    
    # Validate input
    validation = validate_input(payload.input_text)
    
    # If it's valid, no need for suggestions
    if validation.is_valid:
        return Response(
            {"message": "Input is already valid. Use /api/diagrams/generate instead."},
            status=400
        )
    
    # If it's gibberish or too short, don't generate suggestions
    if any("gibberish" in error.lower() or "too short" in error.lower() for error in validation.errors):
        return Response(
            {
                "message": "Cannot generate suggestions for this input",
                "errors": validation.errors,
                "suggestions": validation.suggestions
            },
            status=400
        )
    
    # Generate improvement suggestions using Claude
    suggestions = generate_improvement_suggestions(payload.input_text, validation)
    
    if not suggestions:
        return Response(
            {"message": "Failed to generate suggestions. Please try rephrasing your input."},
            status=500
        )
    
    return SuggestionResponse(
        original_text=payload.input_text,
        validation_issues=validation.errors + validation.questions,
        suggestions=suggestions
    )


@api.post("/diagrams/refine", response=RefinementResponse)
def refine_diagram_endpoint(request, payload: RefinementRequest):
    """
    Refine an existing diagram based on user instructions.
    Supports operations like: remove, add, edit labels, reposition, simplify, enhance.
    """
    from ninja.responses import Response
    
    try:
        result = refine_diagram(
            payload.current_mermaid,
            payload.original_context,
            payload.refinement_instruction
        )
        
        return RefinementResponse(
            updated_mermaid=result["updated_mermaid"],
            changes_made=result["changes_made"],
            explanation=result["explanation"]
        )
        
    except Exception as e:
        return Response(
            {"message": f"Failed to refine diagram: {str(e)}"},
            status=500
        )

"""
Pydantic schemas for API request/response validation.
"""
from ninja import Schema
from typing import List, Optional


class DiagramRequest(Schema):
    input_text: str
    diagram_type: str = "context"


class ValidationResult(Schema):
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    suggestions: List[str]
    questions: List[str] = []


class DiagramResponse(Schema):
    mermaid_code: str
    validation: ValidationResult


class SuggestionOption(Schema):
    title: str
    description: str
    improved_text: str


class SuggestionResponse(Schema):
    original_text: str
    validation_issues: List[str]
    suggestions: List[SuggestionOption]


class RefinementRequest(Schema):
    current_mermaid: str
    original_context: str
    refinement_instruction: str


class RefinementResponse(Schema):
    updated_mermaid: str
    changes_made: List[str]
    explanation: str


class HealthResponse(Schema):
    status: str
    version: str = "1.0.0"

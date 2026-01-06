from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    team_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Diagram Generation Schemas
class DiagramGenerateRequest(BaseModel):
    input_text: str = Field(..., min_length=15, max_length=5000)
    diagram_type: str = Field(default="context", pattern="^(context|container|component)$")
    save_diagram: bool = False
    title: Optional[str] = None


class ValidationResult(BaseModel):
    is_valid: bool
    score: float
    errors: List[dict]
    warnings: List[dict]
    suggestions: List[dict]
    gap_analysis: Optional[dict] = None


class DiagramGenerateResponse(BaseModel):
    diagram_id: Optional[int]
    mermaid_code: str
    validation: ValidationResult
    metadata: dict


# Feedback Schemas
class FeedbackSubmit(BaseModel):
    diagram_id: Optional[int]
    input_id: Optional[int]
    feedback_type: str = Field(..., pattern="^(correction|approval|suggestion|invalid)$")
    feedback_text: Optional[str]
    diagram_quality_rating: Optional[int] = Field(None, ge=1, le=5)
    was_helpful: Optional[bool]


class FeedbackResponse(BaseModel):
    id: int
    feedback_type: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Diagram Schemas
class DiagramResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    mermaid_code: str
    diagram_type: str
    version: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class DiagramListResponse(BaseModel):
    diagrams: List[DiagramResponse]
    total: int
    page: int
    page_size: int


# Analytics Schemas
class UsageStats(BaseModel):
    total_diagrams: int
    total_validations: int
    success_rate: float
    avg_quality_rating: float
    tokens_used: int
    cost_estimate: float


class TeamUsageStats(UsageStats):
    team_id: int
    team_name: str
    quota_remaining: int


# Learning System Schemas
class SimilarPattern(BaseModel):
    pattern_name: str
    similarity_score: float
    example_input: str


class GapAnalysis(BaseModel):
    missing_components: List[str]
    missing_actors: List[str]
    missing_relationships: List[str]
    ambiguous_terms: List[str]
    suggestions: List[str]
    similar_patterns: List[SimilarPattern]


class AutoCompleteRequest(BaseModel):
    partial_input: str = Field(..., min_length=3)
    max_suggestions: int = Field(default=5, ge=1, le=10)


class AutoCompleteResponse(BaseModel):
    suggestions: List[str]
    recognized_patterns: List[str]

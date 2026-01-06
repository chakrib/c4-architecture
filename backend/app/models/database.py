from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, Boolean, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.core.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    team_id = Column(Integer, ForeignKey("teams.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    team = relationship("Team", back_populates="users")
    diagrams = relationship("Diagram", back_populates="user")
    feedback = relationship("UserFeedback", back_populates="user")


class Team(Base):
    __tablename__ = "teams"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    api_quota_per_month = Column(Integer, default=1000)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    users = relationship("User", back_populates="team")
    usage_logs = relationship("UsageLog", back_populates="team")


class ValidatedInput(Base):
    __tablename__ = "validated_inputs"
    
    id = Column(Integer, primary_key=True, index=True)
    input_text = Column(Text, nullable=False)
    embedding = Column(Vector(384))  # Dimension for all-MiniLM-L6-v2
    validation_score = Column(Float)
    user_feedback = Column(String)  # 'valid', 'invalid', 'needs_improvement'
    generated_diagram = Column(Text)
    pattern_type = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))
    
    user = relationship("User")


class Diagram(Base):
    __tablename__ = "diagrams"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    input_text = Column(Text, nullable=False)
    mermaid_code = Column(Text, nullable=False)
    diagram_type = Column(String(50))  # 'context', 'container', 'component'
    version = Column(Integer, default=1)
    parent_id = Column(Integer, ForeignKey("diagrams.id"))  # For versioning
    is_public = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="diagrams")
    parent = relationship("Diagram", remote_side=[id])


class UserFeedback(Base):
    __tablename__ = "user_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    input_id = Column(Integer, ForeignKey("validated_inputs.id"))
    diagram_id = Column(Integer, ForeignKey("diagrams.id"))
    feedback_type = Column(String(50))  # 'correction', 'approval', 'suggestion'
    feedback_text = Column(Text)
    diagram_quality_rating = Column(Integer)  # 1-5
    was_helpful = Column(Boolean)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="feedback")
    validated_input = relationship("ValidatedInput")
    diagram = relationship("Diagram")


class LearnedPattern(Base):
    __tablename__ = "learned_patterns"
    
    id = Column(Integer, primary_key=True, index=True)
    pattern_name = Column(String(100), unique=True, nullable=False)
    keywords = Column(ARRAY(String))
    example_inputs = Column(ARRAY(Text))
    confidence_score = Column(Float, default=0.0)
    usage_count = Column(Integer, default=0)
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UsageLog(Base):
    __tablename__ = "usage_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))
    action = Column(String(50))  # 'generate', 'validate', 'save'
    input_length = Column(Integer)
    tokens_used = Column(Integer)
    cost_estimate = Column(Float)
    success = Column(Boolean)
    error_message = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User")
    team = relationship("Team", back_populates="usage_logs")

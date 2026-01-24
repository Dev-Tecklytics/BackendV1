from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.core.database import Base


class Workflow(Base):
    __tablename__ = "workflows"

    workflow_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.project_id", ondelete="CASCADE"))
    file_id = Column(UUID(as_uuid=True), ForeignKey("files.file_id", ondelete="CASCADE"))

    platform = Column(String, nullable=False)

    complexity_score = Column(Integer)
    complexity_level = Column(String)

    activity_count = Column(Integer)
    nesting_depth = Column(Integer)
    variable_count = Column(Integer)
    invoked_workflows = Column(Integer, default=0)
    has_custom_code = Column(JSON, nullable=True)
    raw_activities = Column(JSON, nullable=True)
    raw_variables = Column(JSON, nullable=True)

    # Migration Analysis Fields
    estimated_effort_hours = Column(Integer, nullable=True)
    compatibility_score = Column(Integer, nullable=True)
    risk_indicators = Column(JSON, nullable=True)
    activity_breakdown = Column(JSON, nullable=True)
    suggestions = Column(JSON, nullable=True)

    # AI-generated fields
    ai_summary = Column(Text, nullable=True)
    ai_recommendations = Column(JSON, nullable=True)

    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    code_reviews = relationship("CodeReview", cascade="all, delete-orphan", passive_deletes=True)

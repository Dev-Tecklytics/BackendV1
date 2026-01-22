from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Workflow(Base):
    __tablename__ = "workflows"

    workflow_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.project_id"))
    file_id = Column(UUID(as_uuid=True), ForeignKey("files.file_id"))

    platform = Column(String, nullable=False)

    complexity_score = Column(Integer)
    complexity_level = Column(String)

    activity_count = Column(Integer)
    nesting_depth = Column(Integer)
    variable_count = Column(Integer)

    # AI-generated fields
    ai_summary = Column(Text, nullable=True)
    ai_recommendations = Column(JSON, nullable=True)

    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())

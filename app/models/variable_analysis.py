from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, JSON, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class VariableAnalysis(Base):
    __tablename__ = "variable_analysis"

    analysis_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.workflow_id", ondelete="CASCADE"), unique=True)

    total_variables = Column(Integer, default=0)
    total_arguments = Column(Integer, default=0)
    unused_variables = Column(JSON, nullable=True)
    unused_arguments = Column(JSON, nullable=True)
    type_mismatches = Column(JSON, nullable=True)
    scope_issues = Column(JSON, nullable=True)
    naming_violations = Column(JSON, nullable=True)

    usage_score = Column(Float, default=0.0)
    type_score = Column(Float, default=0.0)
    naming_score = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)

    analyzed_at = Column(DateTime(timezone=True), server_default=func.now())
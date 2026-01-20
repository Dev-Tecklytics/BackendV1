from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class CodeReview(Base):
    __tablename__ = "code_reviews"

    review_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workflow_id = Column(UUID(as_uuid=True), ForeignKey("workflows.workflow_id"))

    overall_score = Column(Integer)
    grade = Column(String)
    total_issues = Column(Integer)

    findings = Column(JSON)

    reviewed_at = Column(DateTime(timezone=True), server_default=func.now())

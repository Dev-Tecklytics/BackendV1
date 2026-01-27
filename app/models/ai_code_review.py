from sqlalchemy import Column, String, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class AICodeReviewAnalysis(Base):
    __tablename__ = "ai_code_review_analysis"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("code_reviews.review_id", ondelete="CASCADE"), 
        unique=True,
        nullable=False,
        index=True
    )

    # Overall assessment from AI
    overall_assessment = Column(Text, nullable=False)

    # Design patterns identified
    patterns = Column(JSON, nullable=False)  # {identified: [], antiPatterns: []}

    # Optimization opportunities
    optimization_opps = Column(JSON, nullable=False)  # Array of strings

    # Migration risks
    migration_risks = Column(JSON, nullable=False)  # Array of strings

    # Estimated impact scores (0-100)
    estimated_impact = Column(JSON, nullable=False)  # {maintainability, performance, reliability}

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    insights = relationship(
        "AIInsight", 
        back_populates="analysis", 
        cascade="all, delete-orphan",
        lazy="joined"
    )
    review = relationship("CodeReview", backref="ai_analysis_detail")


class AIInsight(Base):
    """
    Individual AI-generated insights for code review.
    Each insight represents a specific finding with detailed context.
    """
    __tablename__ = "ai_insights"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("ai_code_review_analysis.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    # Insight classification
    category = Column(String(100), nullable=False)  # Architecture, Performance, etc.
    severity = Column(String(20), nullable=False)  # Critical, Major, Minor, Info
    title = Column(String(255), nullable=False)

    # Detailed content
    description = Column(Text, nullable=False)
    recommendation = Column(Text, nullable=False)
    reasoning = Column(Text, nullable=False)

    # Metadata
    confidence = Column(Float, nullable=False)  # 0.0 to 1.0
    related_activities = Column(JSON, nullable=True)  # Array of activity names

    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    analysis = relationship("AICodeReviewAnalysis", back_populates="insights")

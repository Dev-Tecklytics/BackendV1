from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class AuditLog(Base):
    """
    Audit log for tracking important system actions.
    Used for compliance, debugging, and security monitoring.
    """
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="SET NULL"), nullable=True)
    
    # Action details
    action = Column(String(100), nullable=False, index=True)  # e.g., "ai_code_review", "workflow_upload"
    resource_type = Column(String(50), nullable=False)  # e.g., "code_review", "workflow"
    resource_id = Column(String(255), nullable=True)  # ID of the affected resource
    
    # Status
    success = Column(Boolean, default=True)
    
    # Additional context
    details = Column(JSON, nullable=True)  # Flexible field for action-specific data
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

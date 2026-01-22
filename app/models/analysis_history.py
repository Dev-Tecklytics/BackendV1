import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from sqlalchemy.sql import func
from sqlalchemy import Enum
import enum

class AnalysisStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class AnalysisHistory(Base):
    __tablename__ = "analysis_history"
    analysis_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    api_key_id = Column(UUID(as_uuid=True), ForeignKey("api_keys.api_key_id"))
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.subscription_id"))
    file_name = Column(String)
    file_path = Column(String, nullable=True)
    file_hash = Column(String, nullable=True, index=True)
    status = Column(Enum(AnalysisStatus),)
    result = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
import uuid
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from sqlalchemy.sql import func

class UsageTracking(Base):
    __tablename__ = "usage_tracking"

    usage_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    api_key_id = Column(UUID(as_uuid=True), ForeignKey("api_keys.api_key_id"))
    endpoint = Column(String)
    response_status = Column(Integer)
    file_size_mb = Column(DECIMAL)
    processing_time_ms = Column(Integer)
    request_timestamp = Column(DateTime(timezone=True), server_default=func.now())
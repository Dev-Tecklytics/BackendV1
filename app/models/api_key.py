import uuid
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.core.database import Base
from sqlalchemy.sql import func

class ApiKey(Base):
    __tablename__ = "api_keys"

    api_key_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    key_hash = Column(String, nullable=False)
    key_prefix = Column(String, nullable=False)
    name = Column(String)
    last_used_at = Column(DateTime)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
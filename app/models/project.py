from sqlalchemy import Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.database import Base

class Project(Base):
    __tablename__ = "projects"

    project_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"), nullable=False)

    name = Column(String(255), nullable=False)
    platform = Column(String(50), nullable=False)  # UiPath | BluePrism
    description = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
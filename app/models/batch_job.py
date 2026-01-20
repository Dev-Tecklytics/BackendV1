from sqlalchemy import Column, String, Integer, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class BatchJob(Base):
    __tablename__ = "batch_jobs"

    batch_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True))
    status = Column(String)

    total_files = Column(Integer)
    processed_files = Column(Integer, default=0)
    results = Column(JSON)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

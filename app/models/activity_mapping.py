from sqlalchemy import Column, String, Integer
from sqlalchemy.dialects.postgresql import UUID
import uuid

from app.core.database import Base


class ActivityMapping(Base):
    __tablename__ = "activity_mappings"

    mapping_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_activity = Column(String)
    target_activity = Column(String)
    compatibility_score = Column(Integer)

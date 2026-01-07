import uuid
from sqlalchemy import Column, String, Boolean, DateTime, Enum, Integer, DECIMAL, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.enums import BillingCycle

class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    plan_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String)
    price = Column(DECIMAL, nullable=False)
    billing_cycle = Column(Enum(BillingCycle), nullable=False)

    api_rate_limit = Column(Integer)
    max_file_size_mb = Column(Integer)
    max_analyses_per_month = Column(Integer)
    features = Column(JSON)

    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
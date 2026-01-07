import uuid
from sqlalchemy import Column, DateTime, Boolean, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.enums import SubscriptionStatus

class Subscription(Base):
    __tablename__ = "subscriptions"

    subscription_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    plan_id = Column(UUID(as_uuid=True), ForeignKey("subscription_plans.plan_id"))
    plan = relationship("SubscriptionPlan")
    status = Column(Enum(SubscriptionStatus), nullable=False)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    auto_renew = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, DECIMAL, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
from app.models.enums import PaymentStatus

class PaymentTransaction(Base):
    __tablename__ = "payment_transactions"
    transaction_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(UUID(as_uuid=True), ForeignKey("subscriptions.subscription_id"))
    amount = Column(DECIMAL, nullable=False)
    currency = Column(String)
    payment_gateway = Column(String)
    gateway_transaction_id = Column(String)
    status = Column(Enum(PaymentStatus), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
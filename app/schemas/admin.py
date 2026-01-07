from pydantic import BaseModel
from datetime import datetime

class AdminSubscriptionResponse(BaseModel):
    subscription_id: str
    user_email: str
    plan_name: str
    status: str
    start_date: datetime | None
    end_date: datetime | None

    class Config:
        from_attributes = True

from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.usage_tracking import UsageTracking
from app.models.subscription_plan import SubscriptionPlan

def check_quota(subscription, api_key, db: Session):
    plan: SubscriptionPlan = subscription.plan

    # Unlimited plan
    if plan.max_analyses_per_month is None:
        return

    # Count today's usage
    today_start = datetime.utcnow().replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    usage_count = (
        db.query(func.count(UsageTracking.usage_id))
        .filter(
            UsageTracking.api_key_id == api_key.api_key_id,
            UsageTracking.request_timestamp >= today_start
        )
        .scalar()
    )

    if usage_count >= plan.max_analyses_per_month:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Subscription quota exceeded"
        )

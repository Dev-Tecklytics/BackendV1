from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.subscription import Subscription
from app.models.enums import SubscriptionStatus

def check_active_subscription(user, db: Session):
    subscription = (
        db.query(Subscription)
        .filter(
            Subscription.user_id == user.user_id,
            Subscription.status.in_([
                SubscriptionStatus.TRIAL,
                SubscriptionStatus.ACTIVE
            ])
        )
        .first()
    )

    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No active subscription"
        )

    return subscription

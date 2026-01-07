from app.core.rate_limiter import enforce_rate_limit
from fastapi import Depends
from sqlalchemy.orm import Session
from app.core.api_key_auth import get_api_key_user
from app.core.subscription_check import check_active_subscription
from app.core.deps import get_db

def get_core_context(
    api_context = Depends(get_api_key_user),
    db: Session = Depends(get_db)
):
    user = api_context["user"]
    api_key = api_context["api_key"]

    # Subscription Check
    subscription = check_active_subscription(user, db)

    # Rate limiting per API key
    enforce_rate_limit(str(api_key.api_key_id))

    # Subscription quota check
    check_quota(subscription, api_key, db)

    return {
        "user": user,
        "api_key": api_key,
        "subscription": subscription
    }

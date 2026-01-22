from app.core.rate_limiter import enforce_rate_limit
from fastapi import Depends, Request, HTTPException, status
from sqlalchemy.orm import Session
from app.core.subscription_check import check_active_subscription
from app.core.quota_check import check_quota
from app.core.deps import get_db
from app.models.api_key import ApiKey
from app.models.user import User

def get_core_context(
    request: Request,
    db: Session = Depends(get_db)
):
    # Get API key from header
    apiKey = request.headers.get("X-API-Key")
    if not apiKey:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key header missing"
        )
    apiKeyRaw = apiKey.split(" : ")
    key_hash = apiKeyRaw[1]
    key_prefix = apiKeyRaw[0]

    # Get API key from db
    api_key = (
        db.query(ApiKey)
        .filter(ApiKey.key_hash == key_hash)
        .filter(ApiKey.key_prefix == key_prefix)
        .filter(ApiKey.is_active == True)
        .first()
    )

    # Check status if API key is valid
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key"
        )

    # Get user from db
    user = db.query(User).filter(User.user_id == api_key.user_id).first()
    
    # Check status if user is valid
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key"
        )

    # Subscription Check
    subscription = check_active_subscription(user, db)

    # Rate limiting per API key
    enforce_rate_limit(str(api_key.api_key_id))

    # Subscription quota check
    check_quota(subscription, api_key, db)

    return {
        "user": user,
        "api_key": api_key,
        "subscription": subscription,
        "headers": dict(request.headers)
    }

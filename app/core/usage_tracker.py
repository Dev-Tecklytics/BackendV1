import time
from fastapi import Request
from sqlalchemy.orm import Session
from app.models.usage_tracking import UsageTracking

def track_usage(
    request: Request,
    context: dict,
    db: Session,
    response_status: int,
    start_time: float
):
    user = context["user"]
    api_key = context["api_key"]

    processing_time_ms = int((time.time() - start_time) * 1000)

    usage = UsageTracking(
        user_id=user.user_id,
        api_key_id=api_key.api_key_id,
        endpoint=request.url.path,
        response_status=response_status,
        processing_time_ms=processing_time_ms
    )

    db.add(usage)
    db.commit()

def increment_ai_calls(db, user_id):
    usage = _get_or_create_usage(db, user_id)
    usage.ai_calls_count = (usage.ai_calls_count or 0) + 1
    db.commit()

def _get_or_create_usage(db: Session, user_id):
    """Get or create usage tracking record for a user."""
    usage = db.query(UsageTracking).filter(UsageTracking.user_id == user_id).first()
    
    if not usage:
        usage = UsageTracking(
            user_id=user_id,
            ai_calls_count=0
        )
        db.add(usage)
        db.commit()
        db.refresh(usage)
    
    return usage

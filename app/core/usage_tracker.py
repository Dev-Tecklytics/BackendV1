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

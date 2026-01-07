from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.core.auth import get_current_user
from app.core.admin_auth import require_admin
from app.core.deps import get_db
from app.models.usage_tracking import UsageTracking
from app.models.user import User

router = APIRouter(
    prefix="/api/v1/admin/analytics",
    tags=["Admin APIs"]
)

@router.get("/usage")
def usage_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Admin check
    require_admin(current_user)

    total_calls = db.query(func.count(UsageTracking.usage_id)).scalar()

    calls_by_endpoint = (
        db.query(
            UsageTracking.endpoint,
            func.count(UsageTracking.usage_id).label("count")
        )
        .group_by(UsageTracking.endpoint)
        .all()
    )

    calls_by_user = (
        db.query(
            UsageTracking.user_id,
            func.count(UsageTracking.usage_id).label("count")
        )
        .group_by(UsageTracking.user_id)
        .all()
    )

    avg_processing_time = db.query(
        func.avg(UsageTracking.processing_time_ms)
    ).scalar()

    return {
        "total_calls": total_calls,
        "calls_by_endpoint": [
            {"endpoint": e, "count": c} for e, c in calls_by_endpoint
        ],
        "calls_by_user": [
            {"user_id": str(u), "count": c} for u, c in calls_by_user
        ],
        "average_processing_time_ms": int(avg_processing_time or 0)
    }

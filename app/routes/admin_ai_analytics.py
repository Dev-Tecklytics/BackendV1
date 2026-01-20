from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.admin_auth import require_admin
from app.services.admin.ai_analytics import (
    get_ai_usage_summary,
    get_top_ai_users,
)

router = APIRouter(
    prefix="/api/v1/admin/ai-analytics",
    tags=["Admin AI Analytics"],
)


@router.get("/summary")
def ai_summary(
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    summary = get_ai_usage_summary(db)
    return {
        "total_ai_calls": summary.total_ai_calls or 0,
        "average_ai_calls_per_user": summary.avg_ai_calls or 0,
    }


@router.get("/top-users")
def top_users(
    db: Session = Depends(get_db),
    _=Depends(require_admin),
):
    users = get_top_ai_users(db)
    return [
        {
            "user_id": str(u.user_id),
            "ai_calls": u.ai_calls_count,
        }
        for u in users
    ]

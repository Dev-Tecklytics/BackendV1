from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.admin_auth import require_admin
from app.core.deps import get_db
from app.models.usage_tracking import UsageTracking

router = APIRouter(
    prefix="/api/v1/admin/usage",
    tags=["Admin APIs"]
)

@router.get("")
def usage_logs(
    db: Session = Depends(get_db),
    admin = Depends(require_admin)
):
    return (
        db.query(UsageTracking)
        .order_by(UsageTracking.request_timestamp.desc())
        .limit(100)
        .all()
    )

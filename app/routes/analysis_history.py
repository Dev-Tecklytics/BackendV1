from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.core_context import get_core_context
from app.core.deps import get_db
from app.models.analysis_history import AnalysisHistory

router = APIRouter(
    prefix="/api/v1/analyze",
    tags=["Analysis APIs"]
)

@router.get("/history")
def analysis_history(
    context = Depends(get_core_context),
    db: Session = Depends(get_db)
):
    user = context["user"]

    history = (
        db.query(AnalysisHistory)
        .filter(AnalysisHistory.user_id == user.user_id)
        .order_by(AnalysisHistory.created_at.desc())
        .all()
    )

    return history

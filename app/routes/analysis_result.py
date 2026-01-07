from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.core_context import get_core_context
from app.core.deps import get_db
from app.models.analysis_history import AnalysisHistory

router = APIRouter(
    prefix="/api/v1/analyze",
    tags=["Analysis APIs"]
)

@router.get("/{analysis_id}")
def get_analysis_result(
    analysis_id: str,
    context = Depends(get_core_context),
    db: Session = Depends(get_db)
):
    analysis = (
        db.query(AnalysisHistory)
        .filter(AnalysisHistory.analysis_id == analysis_id)
        .first()
    )

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return {
        "analysis_id": str(analysis.analysis_id),
        "status": analysis.status,
        "result": analysis.result
    }

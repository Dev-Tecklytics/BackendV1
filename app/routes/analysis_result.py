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

    if analysis.result and isinstance(analysis.result, dict):
        result = analysis.result.copy()
        # Ensure consistency with /uipath
        if "workflow_id" in result and "id" not in result:
            result["id"] = result["workflow_id"]
        
        # Merge status and file_name if not already present in stored result
        if "status" not in result:
            result["status"] = analysis.status
        if "workflowName" not in result:
            result["workflowName"] = analysis.file_name
            
        return result

    return {
        "analysis_id": str(analysis.analysis_id),
        "status": analysis.status,
        "result": analysis.result
    }

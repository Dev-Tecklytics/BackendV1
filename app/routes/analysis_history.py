from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from app.core.core_context import get_core_context
from app.core.deps import get_db
from app.models.analysis_history import AnalysisHistory
from app.models.workflow import Workflow

router = APIRouter(
    prefix="/api/v1/analyze",
    tags=["Analysis APIs"]
)

@router.get("/history")
def analysis_history(
    project_id: Optional[str] = None,
    context = Depends(get_core_context),
    db: Session = Depends(get_db)
):
    user = context["user"]

    if project_id:
        # Join with workflows to filter by project_id
        # Get workflow_ids for this project
        workflow_ids = (
            db.query(Workflow.workflow_id)
            .filter(Workflow.project_id == project_id)
            .all()
        )
        workflow_id_list = [str(wf[0]) for wf in workflow_ids]
        
        # Filter analysis history where result contains matching workflow_id
        history = (
            db.query(AnalysisHistory)
            .filter(AnalysisHistory.user_id == user.user_id)
            .filter(AnalysisHistory.status == "completed")
            .order_by(AnalysisHistory.created_at.desc())
            .all()
        )
        
        # Filter in Python by checking if workflow_id in result matches
        filtered_history = []
        for record in history:
            if record.result and isinstance(record.result, dict):
                result_workflow_id = record.result.get("workflow_id")
                if result_workflow_id in workflow_id_list:
                    filtered_history.append(record)
        
        return filtered_history
    else:
        # Return all analysis history for the user
        history = (
            db.query(AnalysisHistory)
            .filter(AnalysisHistory.user_id == user.user_id)
            .order_by(AnalysisHistory.created_at.desc())
            .all()
        )
        
        return history

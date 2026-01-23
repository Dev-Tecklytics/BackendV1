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
        final_history = []
        for record in history:
            if record.result and isinstance(record.result, dict):
                # Handle both old 'workflow_id' and new 'id' formats
                res = record.result.copy()
                result_workflow_id = res.get("id") or res.get("workflow_id")
                
                if result_workflow_id in workflow_id_list:
                    # Match /uipath structure
                    if "workflow_id" in res and "id" not in res:
                        res["id"] = res["workflow_id"]
                    final_history.append(res)
        
        return final_history
    else:
        # Return all analysis history for the user
        history = (
            db.query(AnalysisHistory)
            .filter(AnalysisHistory.user_id == user.user_id)
            .order_by(AnalysisHistory.created_at.desc())
            .all()
        )
        
        final_history = []
        for record in history:
            if record.result and isinstance(record.result, dict):
                res = record.result.copy()
                # Ensure compatibility with /uipath structure
                if "workflow_id" in res and "id" not in res:
                    res["id"] = res["workflow_id"]
                
                # Add status/filename/id if missing
                if "status" not in res:
                    res["status"] = record.status
                if "workflowName" not in res:
                    res["workflowName"] = record.file_name
                if "platform" not in res:
                    res["platform"] = getattr(record, 'platform', 'Unknown')
                    
                final_history.append(res)
            else:
                # Return a skeleton object for partial/failed analyses
                final_history.append({
                    "id": str(record.analysis_id),
                    "workflowName": record.file_name,
                    "status": record.status,
                    "analyzedAt": record.created_at.isoformat() if record.created_at else None,
                    "platform": "Unknown",
                    "result": record.result  # Could be error details
                })
        
        return final_history

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user
from app.schemas.analysis_compare import (
    PlatformComparisonRequest,
    PlatformComparisonResponse,
)
from app.models.workflow import Workflow
from app.models.activity_mapping import ActivityMapping
from app.services.comparison.comparison_service import compare_platforms

router = APIRouter(
    prefix="/api/v1/analysis",
    tags=["Analysis"],
)


@router.post(
    "/compare-platforms",
    response_model=PlatformComparisonResponse,
)
def compare_platforms_api(
    payload: PlatformComparisonRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    workflow = (
        db.query(Workflow)
        .filter(Workflow.workflow_id == payload.workflow_id)
        .first()
    )

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    mappings = (
        db.query(ActivityMapping)
        .filter(ActivityMapping.source_activity.isnot(None))
        .all()
    )

    return compare_platforms(workflow, mappings)

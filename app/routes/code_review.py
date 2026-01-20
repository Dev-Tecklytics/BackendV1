from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.workflow import Workflow
from app.models.code_review import CodeReview
from app.services.code_review.engine import run_code_review
from app.models.user import User

router = APIRouter(prefix="/api/v1/code-review", tags=["Code Review"])


@router.post("")
def review(
    workflow_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    workflow = db.query(Workflow).filter(Workflow.workflow_id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    metrics = {
        "nesting_depth": workflow.nesting_depth,
        "activity_count": workflow.activity_count,
        "variable_count": workflow.variable_count,
    }

    result = run_code_review(metrics)

    review = CodeReview(
        workflow_id=workflow.workflow_id,
        **result
    )

    db.add(review)
    db.commit()

    return result

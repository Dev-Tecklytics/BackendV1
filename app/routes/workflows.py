from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.file import File
from app.models.workflow import Workflow
from app.services.workflows.complexity import analyze_workflow
from app.models.user import User

router = APIRouter(prefix="/api/v1/workflows", tags=["Workflows"])


@router.post("/analyze")
def analyze(
    file_id: UUID,
    platform: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    file = db.query(File).filter(File.file_id == file_id).first()
    if not file:
        raise HTTPException(status_code=404, detail="File not found")

    result = analyze_workflow(file.file_path)

    workflow = Workflow(
        project_id=file.project_id,
        file_id=file.file_id,
        platform=platform,
        **result,
    )

    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    return result

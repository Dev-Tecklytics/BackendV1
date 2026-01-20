from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.models.batch_job import BatchJob
from app.services.batch.worker import process_batch

router = APIRouter(prefix="/api/v1/batch", tags=["Batch"])


@router.post("")
def create_batch(
    project_id: UUID,
    background: BackgroundTasks,
    db: Session = Depends(get_db),
):
    batch = BatchJob(
        project_id=project_id,
        status="processing",
        total_files=0
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)

    background.add_task(process_batch, db, batch, [])

    return {"batch_id": batch.batch_id}

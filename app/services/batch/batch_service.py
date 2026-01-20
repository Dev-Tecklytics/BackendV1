from sqlalchemy.orm import Session
from fastapi import BackgroundTasks

from app.models.batch_job import BatchJob
from app.models.file import File
from app.services.analysis.analysis_service import run_analysis
from app.services.code_review.code_review_service import run_code_review
from app.core.subscription_check import check_subscription
from app.core.usage_tracker import increment_api_calls


def start_batch(
    db: Session,
    project_id,
    platform: str,
    user_id,
    background: BackgroundTasks,
):
    check_subscription(db, user_id)

    batch = BatchJob(
        project_id=project_id,
        status="processing",
        total_files=0,
        processed_files=0,
    )
    db.add(batch)
    db.commit()
    db.refresh(batch)

    files = db.query(File).filter(File.project_id == project_id).all()
    batch.total_files = len(files)
    db.commit()

    background.add_task(
        _process_batch,
        batch.batch_id,
        files,
        platform,
        user_id,
    )

    return batch


def _process_batch(batch_id, files, platform, user_id):
    """Background task to process batch files - creates its own DB session"""
    from app.core.database import SessionLocal
    
    db = SessionLocal()
    try:
        batch = db.query(BatchJob).filter(BatchJob.batch_id == batch_id).first()
        if not batch:
            return

        for file in files:
            try:
                increment_api_calls(db, user_id)

                workflow = run_analysis(db, file, platform)
                run_code_review(db, workflow, user_id)

                batch.processed_files += 1
                db.commit()
            except Exception as e:
                # Log error but continue processing other files
                print(f"Error processing file {file.file_id}: {e}")
                continue

        batch.status = "completed"
        db.commit()
    finally:
        db.close()

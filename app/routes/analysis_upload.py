import uuid
import shutil
from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.core_context import get_core_context
from app.core.deps import get_db
from app.models.analysis_history import AnalysisHistory, AnalysisStatus
from app.services.analysis_processor import process_analysis_async


router = APIRouter(
    prefix="/api/v1/analyze",
    tags=["Analysis APIs"]
)

@router.post("/upload")
def upload_file_for_analysis(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    context = Depends(get_core_context),
    db: Session = Depends(get_db)
):
    user = context["user"]
    api_key = context["api_key"]
    subscription = context["subscription"]

    analysis_id = uuid.uuid4()

    analysis = AnalysisHistory(
        analysis_id=analysis_id,
        user_id=user.user_id,
        api_key_id=api_key.api_key_id,
        subscription_id=subscription.subscription_id,
        file_name=file.filename,
        status="pending"
    )

    db.add(analysis)
    db.commit()

    # Run analysis asynchronously
    background_tasks.add_task(
        process_analysis,
        analysis_id,
        file.filename
    )

    return {
        "analysis_id": str(analysis_id),
        "status": "pending"
    }

@router.post("/uipath")
def upload_and_analyze(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    context=Depends(get_core_context),
    db: Session = Depends(get_db)
):
    user = context["user"]
    api_key = context["api_key"]
    subscription = context["subscription"]

    analysis_id = uuid.uuid4()

    file_path = f"uploads/{analysis_id}_{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    analysis = AnalysisHistory(
        analysis_id=analysis_id,
        user_id=user.user_id,
        api_key_id=api_key.api_key_id,
        subscription_id=subscription.subscription_id,
        file_name=file.filename,
        status=AnalysisStatus.PENDING
    )

    db.add(analysis)
    db.commit()

    background_tasks.add_task(process_analysis_async, str(analysis_id))

    return {
        "analysis_id": str(analysis_id),
        "status": "PENDING",
        "message": "File uploaded. Analysis started."
    }

@router.get("/{analysis_id}")
def get_analysis_status(
    analysis_id: str,
    context=Depends(get_core_context),
    db: Session = Depends(get_db)
):
    analysis = (
        db.query(AnalysisHistory)
        .filter(AnalysisHistory.analysis_id == analysis_id)
        .first()
    )

    if not analysis:
        return {"detail": "Analysis not found"}

    return {
        "analysis_id": analysis_id,
        "status": analysis.status.value,
        "file_name": analysis.file_name
    }

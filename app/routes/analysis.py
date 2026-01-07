from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.core.core_context import get_core_context
from app.core.deps import get_db
from app.services.analysis_service import perform_analysis

router = APIRouter(
    prefix="/api/v1/analyze",
    tags=["Analysis APIs"]
)

@router.post("")
def analyze(
    file_name: str,
    context = Depends(get_core_context),
    db: Session = Depends(get_db)
):
    user = context["user"]
    api_key = context["api_key"]
    subscription = context["subscription"]

    return perform_analysis(
        user=user,
        api_key=api_key,
        subscription=subscription,
        file_name=file_name,
        db=db
    )

@router.post("/uipath")
def analyze_uipath(
    file: UploadFile = File(...),
    context=Depends(get_core_context)
):
    return {
        "filename": file.filename,
        "status": "processing"
    }

@router.get("/{analysis_id}")
def get_analysis(analysis_id: str):
    return {
        "analysis_id": analysis_id,
        "status": "completed"
    }
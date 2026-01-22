import uuid
import shutil
import hashlib
import json
import re
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from dataclasses import asdict
import logging

from app.core.core_context import get_core_context
from app.core.deps import get_db
from app.models.analysis_history import AnalysisHistory, AnalysisStatus
from app.services.analysis.parser import parse_workflow
from app.services.analysis.metrics import calculate_metrics
from app.services.analysis.complexity import calculate_complexity
from app.services.code_review.engine import run_code_review as run_engine_review

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/analyze",
    tags=["Analysis APIs"]
)

@router.post("/upload")
def upload_file_for_analysis(
    file: UploadFile = File(...),
    context=Depends(get_core_context),
    db: Session = Depends(get_db)
):
    user = context["user"]
    api_key = context["api_key"]
    subscription = context["subscription"]

    analysis_id = uuid.uuid4()

    # Read file for hashing
    file_bytes = file.file.read()
    file.file.seek(0)

    file_hash = hashlib.sha256(file_bytes).hexdigest()

    # Check cache
    existing_analysis = (
        db.query(AnalysisHistory)
        .filter(
            AnalysisHistory.user_id == user.user_id,
            AnalysisHistory.file_hash == file_hash,
            AnalysisHistory.status == AnalysisStatus.COMPLETED
        )
        .order_by(AnalysisHistory.created_at.desc())
        .first()
    )

    if existing_analysis:
        return {
            "analysis_id": str(existing_analysis.analysis_id),
            "status": "completed",
            "file_name": file.filename,
            "result": existing_analysis.result,
            "cached": True
        }

    # Save file
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)

    file_path = upload_dir / f"{analysis_id}_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    analysis = AnalysisHistory(
        analysis_id=analysis_id,
        user_id=user.user_id,
        api_key_id=api_key.api_key_id,
        subscription_id=subscription.subscription_id,
        file_name=file.filename,
        file_path=str(file_path),
        file_hash=file_hash,
        status=AnalysisStatus.IN_PROGRESS
    )

    db.add(analysis)
    db.commit()

    try:
        # Detect platform
        file_ext = Path(file.filename).suffix.lower()
        if file_ext == ".xaml":
            platform = "UiPath"
        elif file_ext in [".bprelease", ".xml"]:
            platform = "Blue Prism"
        else:
            platform = "Unknown"

        # Parse workflow
        parsed_workflow = parse_workflow(str(file_path), platform)

        # Calculate deterministic metrics
        metrics = calculate_metrics(parsed_workflow)

        # Complexity scoring
        complexity = calculate_complexity(metrics)

        # Code review
        review_result = run_engine_review(asdict(metrics))

        result = {
            "platform": platform,
            "metrics": asdict(metrics),
            "complexity": asdict(complexity),
            "code_review": review_result
        }

        analysis.result = result
        analysis.status = AnalysisStatus.COMPLETED
        db.commit()

        return {
            "analysis_id": str(analysis_id),
            "status": "completed",
            "file_name": file.filename,
            "result": result
        }

    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        analysis.status = AnalysisStatus.FAILED
        analysis.result = {
            "error": str(e),
            "error_type": type(e).__name__
        }
        db.commit()

        raise HTTPException(
            status_code=400,
            detail=f"Analysis failed: {str(e)}"
        )

@router.post("/uipath")
def upload_and_analyze_uipath(
    file: UploadFile = File(...),
    context=Depends(get_core_context),
    db: Session = Depends(get_db)
):
    user = context["user"]
    api_key = context["api_key"]
    subscription = context["subscription"]

    analysis_id = uuid.uuid4()

    # Read file for hashing
    file_bytes = file.file.read()
    file.file.seek(0)

    file_hash = hashlib.sha256(file_bytes).hexdigest()

    # Check cache
    existing_analysis = (
        db.query(AnalysisHistory)
        .filter(
            AnalysisHistory.user_id == user.user_id,
            AnalysisHistory.file_hash == file_hash,
            AnalysisHistory.status == AnalysisStatus.COMPLETED
        )
        .order_by(AnalysisHistory.created_at.desc())
        .first()
    )

    if existing_analysis:
        return existing_analysis.result

    # Ensure it's UiPath
    file_ext = Path(file.filename).suffix.lower()
    if file_ext != ".xaml":
        raise HTTPException(
            status_code=400,
            detail="Only .xaml files are supported for UiPath analysis."
        )

    # Save file
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)

    file_path = upload_dir / f"{analysis_id}_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    analysis = AnalysisHistory(
        analysis_id=analysis_id,
        user_id=user.user_id,
        api_key_id=api_key.api_key_id,
        subscription_id=subscription.subscription_id,
        file_name=file.filename,
        file_path=str(file_path),
        file_hash=file_hash,
        status=AnalysisStatus.IN_PROGRESS
    )

    db.add(analysis)
    db.commit()

    try:
        platform = "UiPath"

        # Parse workflow
        parsed_workflow = parse_workflow(str(file_path), platform)

        # Calculate metrics
        metrics = calculate_metrics(parsed_workflow)

        # Complexity scoring
        complexity = calculate_complexity(metrics)

        # Run code review
        review_result = run_engine_review(asdict(metrics))

        result = {
            "workflow_id": str(analysis_id),
            "platform": platform,
            "metrics": {
                "activity_count": metrics.activity_count,
                "variable_count": metrics.variable_count,
                "nesting_depth": metrics.nesting_depth,
                "invoked_workflows": metrics.invoked_workflows,
                "has_custom_code": metrics.has_custom_code
            },
            "complexity": asdict(complexity),
            "code_review": review_result
        }

        analysis.result = result
        analysis.status = AnalysisStatus.COMPLETED
        db.commit()

        return result

    except Exception as e:
        analysis.status = AnalysisStatus.FAILED
        analysis.result = {
            "error": str(e),
            "error_type": type(e).__name__
        }
        db.commit()

        raise HTTPException(
            status_code=400,
            detail=f"Analysis failed: {str(e)}"
        )


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

# --- LEGACY CODE (DO NOT REMOVE) ---
# @router.post("/upload")
# def upload_file_for_analysis(
#     file: UploadFile = File(...),
#     context = Depends(get_core_context),
#     db: Session = Depends(get_db)
# ):
#     ...
#     # (Previous complex logic with falling back to LLM gateway)
#     try:
#         from app.services.analysis.llm_gateway import run_llm_analysis_from_file
#         llm_output = run_llm_analysis_from_file(str(file_path), platform, db, user.user_id)
#         ...
#     except Exception as e:
#         ...

# @router.post("/uipath")
# def upload_and_analyze(
#     file: UploadFile = File(...),
#     context=Depends(get_core_context),
#     db: Session = Depends(get_db)
# ):
#     ...
#     # Comprehensive analysis using genai.Client
#     client = genai.Client(api_key=settings.google_api_key)
#     response = client.models.generate_content(...)
#     ...

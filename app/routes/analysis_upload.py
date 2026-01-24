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
from collections import Counter

from app.core.core_context import get_core_context
from app.core.deps import get_db
from app.models.analysis_history import AnalysisHistory, AnalysisStatus
from app.models.project import Project
from app.models.file import File as FileModel
from app.models.workflow import Workflow
from app.models.code_review import CodeReview
from app.services.analysis.parser import parse_workflow
from app.services.analysis.metrics import calculate_metrics
from app.services.analysis.complexity import calculate_complexity
from app.services.code_review.engine import run_code_review as run_engine_review
from app.services.code_review.code_review_service import run_code_review as run_service_review
from app.services.analysis.activity_mappings import calculate_migration_stats, categorize_activity

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
        cached_result = existing_analysis.result.copy() if existing_analysis.result else {}
        cached_result["cached"] = True
        # Ensure 'id' exists for frontend compatibility if it was stored as 'workflow_id'
        if "workflow_id" in cached_result and "id" not in cached_result:
            cached_result["id"] = cached_result["workflow_id"]
        return cached_result

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

        # 1. Ensure a Project exists
        project = db.query(Project).filter(Project.user_id == user.user_id).first()
        if not project:
            project = Project(
                user_id=user.user_id,
                name="Default Project",
                platform=platform
            )
            db.add(project)
            db.commit()
            db.refresh(project)

        # 2. Create File entry
        db_file = FileModel(
            project_id=project.project_id,
            file_name=file.filename,
            file_path=str(file_path),
            file_size=len(file_bytes)
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)

        # 3. Parse workflow
        parsed_workflow = parse_workflow(str(file_path), platform)

        # 4. Calculate deterministic metrics
        metrics = calculate_metrics(parsed_workflow)

        # 5. Complexity scoring
        complexity = calculate_complexity(metrics)

        # 6. Create Workflow entry
        workflow = Workflow(
            project_id=project.project_id,
            file_id=db_file.file_id,
            platform=platform,
            complexity_score=complexity.score,
            complexity_level=complexity.level,
            activity_count=metrics.activity_count,
            nesting_depth=metrics.nesting_depth,
            variable_count=metrics.variable_count,
            invoked_workflows=metrics.invoked_workflows,
            has_custom_code=metrics.has_custom_code,
            raw_activities=parsed_workflow.raw_activities,
            raw_variables=parsed_workflow.raw_variables
        )
        db.add(workflow)
        db.commit()
        db.refresh(workflow)

        # 7. Run code review (this service saves to DB internally)
        review = run_service_review(db, workflow, user.user_id)

        # 12. Build frontend-expected response
        # Calculate categorized activity breakdown
        categorized = Counter()
        for activity in parsed_workflow.activities:
            categorized[categorize_activity(activity)] += 1
        activity_breakdown = dict(categorized)
        
        # Detect issues from metrics and review
        detected_issues = []
        if metrics.nesting_depth > 3:
            detected_issues.append(f"High nesting depth (level {metrics.nesting_depth})")
        if review.total_issues > 0:
            for finding in review.findings:
                if isinstance(finding, dict):
                    detected_issues.append(finding.get("message", "Unknown issue"))
        if metrics.has_custom_code:
            detected_issues.append("Contains custom code/scripts")
        
        # Generate suggestions from code review findings
        suggestions = []
        if review.findings:
            for idx, finding in enumerate(review.findings, 1):
                if isinstance(finding, dict):
                    suggestions.append({
                        "id": idx,
                        "priority": finding.get("severity", "medium").lower(),
                        "title": finding.get("message", "Code Quality Issue"),
                        "description": finding.get("recommendation", "Review and refactor"),
                        "impact": finding.get("impact", "Medium"),
                        "effort": finding.get("effort", "Medium"),
                        "benefits": ["Improved maintainability", "Better code quality"],
                        "implementation_steps": [finding.get("recommendation", "Review code")]
                    })
        
        # Estimate migration effort using the comprehensive mapping service
        stats = calculate_migration_stats(parsed_workflow.activities)
        effort_hours = stats["totalEffortHours"]
        compatibility_score = stats["compatibilityScore"]

        # 12. Update Workflow entry with analysis results
        workflow.activity_breakdown = activity_breakdown
        workflow.risk_indicators = detected_issues if detected_issues else ["No major issues detected"]
        workflow.estimated_effort_hours = effort_hours
        workflow.compatibility_score = compatibility_score
        workflow.suggestions = suggestions
        db.commit()

        result = {
            "id": str(workflow.workflow_id),
            "workflowName": file.filename,
            "platform": platform,

            # Flattened fields (VERY IMPORTANT)
            "complexityScore": float(complexity.score),
            "complexityLevel": complexity.level,
            "totalActivities": metrics.activity_count,
            "estimatedEffortHours": effort_hours,
            "compatibilityScore": compatibility_score,

            "riskIndicators": workflow.risk_indicators,
            "activityBreakdown": activity_breakdown,

            "analyzedAt": workflow.analyzed_at.isoformat() if workflow.analyzed_at else datetime.utcnow().isoformat(),

            # Optional (detail page use)
            "suggestions": suggestions,
        }

        analysis.result = result
        analysis.status = AnalysisStatus.COMPLETED
        db.commit()

        return result

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

    # Read file & compute hash
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
        cached_result = existing_analysis.result.copy() if existing_analysis.result else {}
        cached_result["cached"] = True

        if "workflow_id" in cached_result and "id" not in cached_result:
            cached_result["id"] = cached_result["workflow_id"]

        return cached_result

    # Validate extension
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

        # Ensure project exists
        project = db.query(Project).filter(Project.user_id == user.user_id).first()
        if not project:
            project = Project(
                user_id=user.user_id,
                name="Default Project",
                platform=platform
            )
            db.add(project)
            db.commit()
            db.refresh(project)

        # Create file record
        db_file = FileModel(
            project_id=project.project_id,
            file_name=file.filename,
            file_path=str(file_path),
            file_size=len(file_bytes)
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)

        # Parse workflow
        parsed_workflow = parse_workflow(str(file_path), platform)

        # Metrics & complexity
        metrics = calculate_metrics(parsed_workflow)
        complexity = calculate_complexity(metrics)
        # Create workflow DB record

        workflow = Workflow(
            project_id=project.project_id,
            file_id=db_file.file_id,
            platform=platform,
            complexity_score=complexity.score,
            complexity_level=complexity.level,
            activity_count=len(parsed_workflow.activities),
            nesting_depth=metrics.nesting_depth,
            variable_count=metrics.variable_count,
            invoked_workflows=metrics.invoked_workflows,
            has_custom_code=metrics.has_custom_code,
            raw_activities=parsed_workflow.raw_activities,
            raw_variables=parsed_workflow.raw_variables
        )

        db.add(workflow)
        db.commit()
        db.refresh(workflow)
        # Code review
        review = run_service_review(db, workflow, user.user_id)

        # Categorized Activity Breakdown using mapping service
        categorized = Counter()
        for activity in parsed_workflow.activities:
            categorized[categorize_activity(activity)] += 1

        activity_breakdown = dict(categorized)

        # Detect Issues
        detected_issues = []

        if metrics.nesting_depth > 3:
            detected_issues.append(f"High nesting depth (level {metrics.nesting_depth})")

        if review.total_issues > 0:
            for finding in review.findings:
                if isinstance(finding, dict):
                    detected_issues.append(finding.get("message", "Unknown issue"))

        if metrics.has_custom_code:
            detected_issues.append("Contains custom code/scripts")
        # Suggestions
        suggestions = []
        if review.findings:
            for idx, finding in enumerate(review.findings, 1):
                if isinstance(finding, dict):
                    suggestions.append({
                        "id": idx,
                        "priority": finding.get("severity", "medium").lower(),
                        "title": finding.get("message", "Code Quality Issue"),
                        "description": finding.get("recommendation", "Review and refactor"),
                        "impact": finding.get("impact", "Medium"),
                        "effort": finding.get("effort", "Medium"),
                        "benefits": ["Improved maintainability", "Better code quality"],
                        "implementation_steps": [finding.get("recommendation", "Review code")]
                    })

        # Effort Estimation using the comprehensive mapping service
        stats = calculate_migration_stats(parsed_workflow.activities)
        effort_hours = stats["totalEffortHours"]
        compatibility_score = stats["compatibilityScore"]
        # Final Response & Persist to Workflow Table
        workflow.activity_breakdown = activity_breakdown
        workflow.risk_indicators = detected_issues or ["No major issues detected"]
        workflow.estimated_effort_hours = effort_hours
        workflow.compatibility_score = compatibility_score
        workflow.suggestions = suggestions
        db.commit()

        result = {
            "id": str(workflow.workflow_id),
            "workflowName": file.filename,
            "platform": platform,
            "complexityScore": float(complexity.score),
            "complexityLevel": complexity.level,
            "totalActivities": len(parsed_workflow.activities),
            "estimatedEffortHours": effort_hours,
            "compatibilityScore": compatibility_score,
            "riskIndicators": workflow.risk_indicators,
            "activityBreakdown": activity_breakdown,
            "analyzedAt": workflow.analyzed_at.isoformat()
                if workflow.analyzed_at
                else datetime.utcnow().isoformat(),
            "suggestions": suggestions
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


# @router.post("/uipath")
# def upload_and_analyze_uipath(
#     file: UploadFile = File(...),
#     context=Depends(get_core_context),
#     db: Session = Depends(get_db)
# ):
#     user = context["user"]
#     api_key = context["api_key"]
#     subscription = context["subscription"]

#     analysis_id = uuid.uuid4()

#     # Read file for hashing
#     file_bytes = file.file.read()
#     file.file.seek(0)

#     file_hash = hashlib.sha256(file_bytes).hexdigest()

#     # Check cache
#     existing_analysis = (
#         db.query(AnalysisHistory)
#         .filter(
#             AnalysisHistory.user_id == user.user_id,
#             AnalysisHistory.file_hash == file_hash,
#             AnalysisHistory.status == AnalysisStatus.COMPLETED
#         )
#         .order_by(AnalysisHistory.created_at.desc())
#         .first()
#     )

#     if existing_analysis:
#         # Return cached result with cached flag
#         cached_result = existing_analysis.result.copy() if existing_analysis.result else {}
#         cached_result["cached"] = True
        
#         # Ensure 'id' exists for frontend compatibility if it was stored as 'workflow_id'
#         if "workflow_id" in cached_result and "id" not in cached_result:
#             cached_result["id"] = cached_result["workflow_id"]

#         logger.info(f"CACHE HIT for file hash: {file_hash[:16]}...")
#         logger.info(f"Returning cached response: id={cached_result.get('id')}, platform={cached_result.get('platform')}")
#         print(f"\n{'='*80}\nCACHED RESPONSE:\n{json.dumps(cached_result, indent=2)}\n{'='*80}\n")
#         return cached_result

#     # Ensure it's UiPath
#     file_ext = Path(file.filename).suffix.lower()
#     if file_ext != ".xaml":
#         raise HTTPException(
#             status_code=400,
#             detail="Only .xaml files are supported for UiPath analysis."
#         )

#     # Save file
#     upload_dir = Path("uploads")
#     upload_dir.mkdir(exist_ok=True)

#     file_path = upload_dir / f"{analysis_id}_{file.filename}"

#     with open(file_path, "wb") as buffer:
#         shutil.copyfileobj(file.file, buffer)

#     analysis = AnalysisHistory(
#         analysis_id=analysis_id,
#         user_id=user.user_id,
#         api_key_id=api_key.api_key_id,
#         subscription_id=subscription.subscription_id,
#         file_name=file.filename,
#         file_path=str(file_path),
#         file_hash=file_hash,
#         status=AnalysisStatus.IN_PROGRESS
#     )

#     db.add(analysis)
#     db.commit()

#     try:
#         platform = "UiPath"

#         # 1. Ensure a Project exists
#         project = db.query(Project).filter(Project.user_id == user.user_id).first()
#         if not project:
#             project = Project(
#                 user_id=user.user_id,
#                 name="Default Project",
#                 platform=platform
#             )
#             db.add(project)
#             db.commit()
#             db.refresh(project)

#         # 2. Create File entry
#         db_file = FileModel(
#             project_id=project.project_id,
#             file_name=file.filename,
#             file_path=str(file_path),
#             file_size=len(file_bytes)
#         )
#         db.add(db_file)
#         db.commit()
#         db.refresh(db_file)

#         # 3. Parse workflow
#         parsed_workflow = parse_workflow(str(file_path), platform)

#         # 4. Calculate metrics
#         metrics = calculate_metrics(parsed_workflow)

#         # 5. Complexity scoring
#         complexity = calculate_complexity(metrics)

#         # 6. Create Workflow entry
#         workflow = Workflow(
#             project_id=project.project_id,
#             file_id=db_file.file_id,
#             platform=platform,
#             complexity_score=complexity.score,
#             complexity_level=complexity.level,
#             activity_count=metrics.activity_count,
#             nesting_depth=metrics.nesting_depth,
#             variable_count=metrics.variable_count,
#             invoked_workflows=metrics.invoked_workflows,
#             has_custom_code=metrics.has_custom_code
#         )
#         db.add(workflow)
#         db.commit()
#         db.refresh(workflow)

#         # 7. Run code review (this service saves to DB internally)
#         review = run_service_review(db, workflow, user.user_id)

#         # 8. Calculate activity breakdown
#         from collections import Counter
#         activity_breakdown = dict(Counter(parsed_workflow.activities))
        
#         # 9. Detect issues from metrics and review
#         detected_issues = []
#         if metrics.nesting_depth > 3:
#             detected_issues.append(f"High nesting depth (level {metrics.nesting_depth})")
#         if review.total_issues > 0:
#             for finding in review.findings:
#                 if isinstance(finding, dict):
#                     detected_issues.append(finding.get("message", "Unknown issue"))
#         if metrics.has_custom_code:
#             detected_issues.append("Contains custom code/scripts")
        
#         # 10. Generate suggestions from code review findings
#         suggestions = []
#         if review.findings:
#             for idx, finding in enumerate(review.findings, 1):
#                 if isinstance(finding, dict):
#                     suggestions.append({
#                         "id": idx,
#                         "priority": finding.get("severity", "medium").lower(),
#                         "title": finding.get("message", "Code Quality Issue"),
#                         "description": finding.get("recommendation", "Review and refactor"),
#                         "impact": finding.get("impact", "Medium"),
#                         "effort": finding.get("effort", "Medium"),
#                         "benefits": ["Improved maintainability", "Better code quality"],
#                         "implementation_steps": [finding.get("recommendation", "Review code")]
#                     })
        
#         # 11. Estimate migration effort (basic formula)
#         base_hours = 2
#         complexity_multiplier = complexity.score / 20  # Scale complexity score
#         effort_hours = round(base_hours + complexity_multiplier + (metrics.invoked_workflows * 0.5), 1)
        
#         # 12. Build frontend-expected response
#         result = {
#             "id": str(workflow.workflow_id),
#             "workflowName": file.filename,
#             "platform": platform,

#             # Flattened fields (VERY IMPORTANT)
#             "complexityScore": float(complexity.score),
#             "complexityLevel": complexity.level,
#             "totalActivities": metrics.activity_count,
#             "estimatedEffortHours": effort_hours,

#             "riskIndicators": detected_issues if detected_issues else ["No major issues detected"],
#             "activityBreakdown": activity_breakdown,

#             "analyzedAt": workflow.analyzed_at.isoformat() if workflow.analyzed_at else datetime.utcnow().isoformat(),

#             # Optional (detail page use)
#             "suggestions": suggestions,
#         }

#         print(result)
#         analysis.result = result
#         analysis.status = AnalysisStatus.COMPLETED
#         db.commit()

#         return result

#     except Exception as e:
#         analysis.status = AnalysisStatus.FAILED
#         analysis.result = {
#             "error": str(e),
#             "error_type": type(e).__name__
#         }
#         db.commit()

#         raise HTTPException(
#             status_code=400,
#             detail=f"Analysis failed: {str(e)}"
#         )


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

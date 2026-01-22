import uuid
import shutil
import os
import json
import re
import hashlib
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from google import genai

from app.core.core_context import get_core_context
from app.core.deps import get_db
from app.core.config import settings
from app.models.analysis_history import AnalysisHistory, AnalysisStatus
from app.services.analysis.parser import parse_workflow
from app.services.analysis.metrics import calculate_metrics
from app.services.analysis.llm_gateway import run_llm_analysis
from app.domain.llm_contracts import LLMInput
import logging

# Configure gemini at module level or inside route
# genai.configure no longer used in new SDK

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/analyze",
    tags=["Analysis APIs"]
)

@router.post("/upload")
def upload_file_for_analysis(
    file: UploadFile = File(...),
    context = Depends(get_core_context),
    db: Session = Depends(get_db)
):
    user = context["user"]
    api_key = context["api_key"]
    subscription = context["subscription"]

    analysis_id = uuid.uuid4()
    
    # Read file content for hashing
    file_bytes = file.file.read()
    file.file.seek(0)  # Reset for later saving
    
    file_hash = hashlib.sha256(file_bytes).hexdigest()
    
    # Check for existing completed analysis
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
        logger.info(f"Duplicate file detected for user {user.user_id} in /upload. Returning cached result.")
        return {
            "analysis_id": str(existing_analysis.analysis_id),
            "status": "completed",
            "file_name": file.filename,
            "result": existing_analysis.result,
            "cached": True
        }

    # Create uploads directory if it doesn't exist
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    
    # Save file to disk
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
        # Detect platform from file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext == ".xaml":
            platform = "UiPath"
        elif file_ext == ".bprelease" or file_ext == ".xml":
            platform = "Blue Prism"
        else:
            platform = "Unknown"

        # Try direct LLM analysis first (simpler and more robust)
        try:
            from app.services.analysis.llm_gateway import run_llm_analysis_from_file
            logger.info(f"Using direct LLM analysis for {analysis_id}")
            llm_output = run_llm_analysis_from_file(str(file_path), platform, db, user.user_id)
            
            # Store results
            result = {
                "platform": platform,
                "summary": llm_output.summary,
                "risks": llm_output.risks,
                "optimization_suggestions": llm_output.optimization_suggestions,
                "migration_notes": llm_output.migration_notes,
                "analysis_method": "direct_llm"
            }
        except Exception as direct_error:
            logger.warning(f"Direct LLM analysis failed, falling back to parsing: {str(direct_error)}")

        # Parse the workflow file
        logger.info(f"Parsing workflow file: {file_path}")
        parsed_workflow = parse_workflow(str(file_path), platform)

        # Calculate metrics
        logger.info(f"Calculating metrics for {analysis_id}")
        metrics = calculate_metrics(parsed_workflow)

        # Prepare LLM input
        llm_input = LLMInput(
            platform=platform,
            metrics=metrics,
            activity_summary={}
        )

        # Call LLM for analysis
        logger.info(f"Calling LLM for analysis {analysis_id}")
        llm_output = run_llm_analysis(llm_input, db, user.user_id, file_path=str(file_path))

        # Store results
        result = {
            "platform": platform,
            "metrics": {
                "activity_count": metrics.activity_count,
                "variable_count": metrics.variable_count,
                "nesting_depth": metrics.nesting_depth,
                "invoked_workflows": metrics.invoked_workflows,
                "has_custom_code": metrics.has_custom_code
            },
            "summary": llm_output.summary,
            "risks": llm_output.risks,
            "optimization_suggestions": llm_output.optimization_suggestions,
            "migration_notes": llm_output.migration_notes
        }

        analysis.result = result
        analysis.status = AnalysisStatus.COMPLETED
        db.commit()
        
        logger.info(f"Analysis {analysis_id} completed successfully")

        # Return full analysis results
        return {
            "analysis_id": str(analysis_id),
            "status": "completed",
            "file_name": file.filename,
            "result": result
        }

    except Exception as e:
        logger.error(f"Analysis {analysis_id} failed: {str(e)}", exc_info=True)
        analysis.status = AnalysisStatus.FAILED
        
        # Provide user-friendly error messages
        error_message = str(e)
        if "tag mismatch" in error_message.lower() or "xml" in error_message.lower():
            user_message = "The uploaded file contains invalid XML structure. Please ensure the workflow file is not corrupted and was exported correctly from your RPA tool."
        elif "file not found" in error_message.lower():
            user_message = "The uploaded file could not be found. Please try uploading again."
        elif "permission" in error_message.lower():
            user_message = "Permission denied while accessing the file. Please try again."
        else:
            user_message = f"Analysis failed: {error_message}"
        
        analysis.result = {
            "error": error_message,
            "error_type": type(e).__name__,
            "user_message": user_message
        }
        db.commit()
        
        raise HTTPException(
            status_code=400,  # Changed from 500 to 400 for client errors
            detail=user_message
        )

@router.post("/uipath")
def upload_and_analyze(
    file: UploadFile = File(...),
    context=Depends(get_core_context),
    db: Session = Depends(get_db)
):
    user = context["user"]
    api_key = context["api_key"]
    subscription = context["subscription"]

    analysis_id = uuid.uuid4()
    
    # Read file content for hashing
    file_bytes = file.file.read()
    file.file.seek(0)  # Reset for later saving
    
    file_hash = hashlib.sha256(file_bytes).hexdigest()
    
    # Check for existing completed analysis
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
        logger.info(f"Duplicate file detected for user {user.user_id}. Returning cached result.")
        return existing_analysis.result

    # Create uploads directory if it doesn't exist
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
        # Read file content for analysis
        file_content = file_bytes.decode('utf-8', errors='ignore')
        
        # Get file size
        file_size_kb = len(file_content.encode('utf-8')) / 1024
        
        # Truncate if too large
        # if len(file_content) > 30000:
        #     file_content = file_content[:30000] + "\n... (truncated)"
        
        # Use comprehensive analysis prompt
        from app.services.analysis.prompts import COMPREHENSIVE_ANALYSIS_PROMPT
        prompt = COMPREHENSIVE_ANALYSIS_PROMPT.format(file_content=file_content)
        
        client = genai.Client(api_key=settings.google_api_key)
        
        from app.core.usage_tracker import increment_ai_calls
        increment_ai_calls(db, user.user_id)
        
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
            config={
                "temperature": 0.3,
                "max_output_tokens": 2048,
                "response_mime_type": "application/json"
            },
        )
        
        raw_text = response.text.strip()
        logger.info(f"Comprehensive analysis response: {raw_text[:200]}...")
        
        # Clean up response
        cleaned_text = raw_text
        if cleaned_text.startswith("```"):
            cleaned_text = re.sub(r'^```(?:json)?\s*', '', cleaned_text)
            cleaned_text = re.sub(r'\s*```$', '', cleaned_text)
            cleaned_text = cleaned_text.strip()
        
        result = json.loads(cleaned_text)
        
        # Add workflow_id and analyzed_at
        result["workflow_id"] = str(analysis_id)
        if "analysis" in result:
            result["analysis"]["analyzed_at"] = datetime.now().isoformat()
            result["analysis"]["file_size_kb"] = round(file_size_kb, 2)
        
        # Store in database
        analysis.result = result
        analysis.status = AnalysisStatus.COMPLETED
        db.commit()
        
        logger.info(f"Comprehensive analysis {analysis_id} completed successfully")
        
        return result
        
    except Exception as e:
        logger.error(f"Comprehensive analysis {analysis_id} failed: {str(e)}", exc_info=True)
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

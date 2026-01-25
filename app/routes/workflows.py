from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.file import File
from app.models.workflow import Workflow
from app.models.project import Project
from app.services.workflows.complexity import analyze_workflow
from app.services.workflows.workflow_llm_gateway import run_workflow_llm_analysis
from app.models.user import User

router = APIRouter(prefix="/api/v1/workflows", tags=["Workflows"])


class WorkflowUpdateRequest(BaseModel):
    platform: Optional[str] = None
    complexity_score: Optional[int] = None
    complexity_level: Optional[str] = None
    activity_count: Optional[int] = None
    nesting_depth: Optional[int] = None
    variable_count: Optional[int] = None
    ai_summary: Optional[str] = None
    ai_recommendations: Optional[list] = None
    estimated_effort_hours: Optional[float] = None
    compatibility_score: Optional[int] = None
    risk_indicators: Optional[list] = None
    activity_breakdown: Optional[dict] = None
    suggestions: Optional[list] = None


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

    # Step 1: Local complexity analysis
    result = analyze_workflow(file.file_path)

    # Step 2: AI-powered analysis (with graceful fallback)
    ai_result = {}
    try:
        ai_result = run_workflow_llm_analysis(
            metrics=result,
            platform=platform,
            db=db,
            user_id=user.user_id
        )
    except Exception as e:
        # Graceful degradation - continue without AI insights
        print(f"AI analysis failed: {e}")
        ai_result = {
            "ai_summary": None,
            "ai_recommendations": None,
        }

    # Step 3: Create workflow record with both local and AI results
    workflow = Workflow(
        project_id=file.project_id,
        file_id=file.file_id,
        platform=platform,
        **result,
        ai_summary=ai_result.get("ai_summary"),
        ai_recommendations=ai_result.get("ai_recommendations"),
    )

    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    # Return combined results
    return {
        "workflow_id": str(workflow.workflow_id),
        **result,
        "ai_summary": ai_result.get("ai_summary"),
        "ai_recommendations": ai_result.get("ai_recommendations"),
    }


@router.get("/project")
def get_workflows_by_project(
    project_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get workflows for a specific project ID."""
    project = db.query(Project).filter(Project.project_id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    workflows = db.query(Workflow).filter(Workflow.project_id == project_id).all()
    
    return [
        {
            "id": str(w.workflow_id),
            "workflowName": w.workflow_name or "Unknown workflow",
            "platform": w.platform,
            "complexityScore": w.complexity_score or 0,
            "complexityLevel": w.complexity_level or "Unknown",
            "totalActivities": w.activity_count or 0,
            "estimatedEffortHours": w.estimated_effort_hours or 0,
            "riskIndicators": w.risk_indicators or [],
            "activityBreakdown": w.activity_breakdown or {},
            "analyzedAt": w.analyzed_at.isoformat() if w.analyzed_at else "",
            "project": {
                "id": str(project.project_id),
                "name": project.name,
                "platform": project.platform
            }
        }
        for w in workflows
    ]


@router.get("/{workflow_id}")
def get_workflow(
    workflow_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get a specific workflow by ID."""
    workflow = db.query(Workflow).filter(Workflow.workflow_id == workflow_id).first()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    return {
        "workflow_id": str(workflow.workflow_id),
        "project_id": str(workflow.project_id),
        "file_id": str(workflow.file_id),
        "platform": workflow.platform,
        "complexity_score": workflow.complexity_score,
        "complexity_level": workflow.complexity_level,
        "activity_count": workflow.activity_count,
        "nesting_depth": workflow.nesting_depth,
        "variable_count": workflow.variable_count,
        "ai_summary": workflow.ai_summary,
        "ai_recommendations": workflow.ai_recommendations,
        "analyzed_at": workflow.analyzed_at.isoformat() if workflow.analyzed_at else None,
    }


@router.get("")
def list_workflows(
    project_id: Optional[UUID] = None,
    platform: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """List workflows with optional filtering."""
    query = db.query(Workflow)
    
    if project_id:
        query = query.filter(Workflow.project_id == project_id)
    
    if platform:
        query = query.filter(Workflow.platform == platform)
    
    workflows = query.offset(skip).limit(limit).all()
    
    return {
        "workflows": [
            {
                "workflow_id": str(w.workflow_id),
                "project_id": str(w.project_id),
                "file_id": str(w.file_id),
                "platform": w.platform,
                "complexity_score": w.complexity_score,
                "complexity_level": w.complexity_level,
                "activity_count": w.activity_count,
                "nesting_depth": w.nesting_depth,
                "variable_count": w.variable_count,
                "ai_summary": w.ai_summary,
                "ai_recommendations": w.ai_recommendations,
                "estimatedEffortHours": w.estimated_effort_hours,
                "compatibilityScore": w.compatibility_score,
                "riskIndicators": w.risk_indicators,
                "activityBreakdown": w.activity_breakdown,
                "suggestions": w.suggestions,
                "analyzedAt": w.analyzed_at.isoformat() if w.analyzed_at else None,
            }
            for w in workflows
        ]
    }


@router.patch("/name")
def update_workflow_name(
    workflow_id: UUID,
    workflow_name: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update workflow name."""
    workflow = db.query(Workflow).filter(Workflow.workflow_id == workflow_id).first()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    workflow.workflow_name = workflow_name
    db.commit()
    
    return {
        "message": "Workflow name updated successfully",
        "workflow_id": workflow_id,
        "workflow_name": workflow_name
    }


@router.put("/{workflow_id}")
def update_workflow(
    workflow_id: UUID,
    update_data: WorkflowUpdateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Update a workflow's details."""
    workflow = db.query(Workflow).filter(Workflow.workflow_id == workflow_id).first()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Update only provided fields
    update_dict = update_data.dict(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(workflow, field, value)
    
    db.commit()
    db.refresh(workflow)
    
    return {
        "workflow_id": str(workflow.workflow_id),
        "project_id": str(workflow.project_id),
        "file_id": str(workflow.file_id),
        "platform": workflow.platform,
        "complexity_score": workflow.complexity_score,
        "complexity_level": workflow.complexity_level,
        "activity_count": workflow.activity_count,
        "nesting_depth": workflow.nesting_depth,
        "variable_count": workflow.variable_count,
        "ai_summary": workflow.ai_summary,
        "ai_recommendations": workflow.ai_recommendations,
        "analyzed_at": workflow.analyzed_at.isoformat() if workflow.analyzed_at else None,
    }


@router.delete("/{workflow_id}")
def delete_workflow(
    workflow_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Delete a workflow."""
    workflow = db.query(Workflow).filter(Workflow.workflow_id == workflow_id).first()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    db.delete(workflow)
    db.commit()
    
    return {
        "message": "Workflow deleted successfully",
        "workflow_id": str(workflow_id)
    }

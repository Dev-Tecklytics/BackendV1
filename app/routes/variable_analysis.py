from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.workflow import Workflow
from app.models.variable_analysis import VariableAnalysis
from app.models.user import User

router = APIRouter(prefix="/api/v1/workflows", tags=["Variable Analysis"])


@router.post("/{workflow_id}/variable-analysis")
def analyze_variables(
    workflow_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Perform variable analysis on a workflow."""
    workflow = db.query(Workflow).filter(Workflow.workflow_id == workflow_id).first()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # Check if analysis already exists
    existing = db.query(VariableAnalysis).filter(
        VariableAnalysis.workflow_id == workflow_id
    ).first()
    
    if existing:
        return {"analysis": existing}
    
    # Mock analysis results (replace with actual analysis logic)
    analysis_result = {
        "totalVariables": workflow.variable_count or 0,
        "totalArguments": 0,
        "unusedVariables": [],
        "unusedArguments": [],
        "typeMismatches": [],
        "scopeIssues": [],
        "namingViolations": [],
        "usageScore": 85.0,
        "typeScore": 90.0,
        "namingScore": 75.0,
        "overallScore": 83.3
    }
    
    # Store results
    analysis = VariableAnalysis(
        workflow_id=workflow_id,
        total_variables=analysis_result["totalVariables"],
        total_arguments=analysis_result["totalArguments"],
        unused_variables=analysis_result["unusedVariables"],
        unused_arguments=analysis_result["unusedArguments"],
        type_mismatches=analysis_result["typeMismatches"],
        scope_issues=analysis_result["scopeIssues"],
        naming_violations=analysis_result["namingViolations"],
        usage_score=analysis_result["usageScore"],
        type_score=analysis_result["typeScore"],
        naming_score=analysis_result["namingScore"],
        overall_score=analysis_result["overallScore"]
    )
    
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    
    return {"analysis": analysis}


@router.get("/{workflow_id}/variable-analysis")
def get_variable_analysis(
    workflow_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get variable analysis for a workflow."""
    workflow = db.query(Workflow).filter(Workflow.workflow_id == workflow_id).first()
    
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    analysis = db.query(VariableAnalysis).filter(
        VariableAnalysis.workflow_id == workflow_id
    ).first()
    
    if not analysis:
        raise HTTPException(
            status_code=404, 
            detail="Variable analysis not found. Please run analysis first."
        )
    
    return {"analysis": analysis}
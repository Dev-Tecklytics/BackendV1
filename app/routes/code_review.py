from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.workflow import Workflow
from app.models.code_review import CodeReview
from app.services.code_review.comprehensive_rules import perform_code_review, get_severity_counts
from app.services.code_review.code_review_llm_gateway import run_code_review_llm
from app.services.custom_rules.engine import run_custom_rules
from app.models.custom_rules import CustomRule
from app.models.user import User

router = APIRouter(prefix="/api/v1/code-review", tags=["Code Review"])


@router.post("")
def review(
    workflow_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Comprehensive Code Review Engine
    
    Workflow:
    1. Fetch workflow with full DNA (activities, variables)
    2. Run comprehensive built-in rules (50+ checks)
    3. Run custom user-defined rules
    4. Calculate weighted scores
    5. Persist results
    6. Return detailed findings
    """
    workflow = db.query(Workflow).filter(Workflow.workflow_id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Check for existing review (caching)
    existing_review = db.query(CodeReview).filter(
        CodeReview.workflow_id == workflow_id
    ).first()
    
    if existing_review:
        # Return cached result
        return {
            "review_id": str(existing_review.review_id),
            "overall_score": existing_review.overall_score,
            "grade": existing_review.grade,
            "total_issues": existing_review.total_issues,
            "findings": existing_review.findings,
            "ai_issues": existing_review.ai_issues,
            "ai_best_practices": existing_review.ai_best_practices,
            "ai_security_concerns": existing_review.ai_security_concerns,
            "ai_refactoring_suggestions": existing_review.ai_refactoring_suggestions,
            "cached": True
        }

    # Prepare workflow data for review
    workflow_data = {
        "workflowName": workflow.file.file_name if hasattr(workflow, 'file') else "Unknown",
        "nestingDepth": workflow.nesting_depth,
        "activityCount": workflow.activity_count,
        "variables": workflow.raw_variables or []
    }
    
    activities = workflow.raw_activities or []

    # Step 1: Run comprehensive built-in rules
    review_result = perform_code_review(
        platform=workflow.platform,
        workflow=workflow_data,
        activities=activities
    )
    
    findings = review_result['findings']
    category_scores = review_result['categoryScores']
    overall_score = review_result['overallScore']
    quality_grade = review_result['qualityGrade']

    # Step 2: Run custom user-defined rules
    active_custom_rules = db.query(CustomRule).filter(
        CustomRule.user_id == user.user_id,
        CustomRule.is_active == True
    ).all()
    
    if active_custom_rules:
        custom_metrics = {
            "activity_count": workflow.activity_count,
            "nesting_depth": workflow.nesting_depth,
            "variable_count": workflow.variable_count
        }
        custom_findings = run_custom_rules(active_custom_rules, custom_metrics)
        
        # Merge custom findings into main findings list
        for custom_finding in custom_findings:
            findings.append({
                "category": "Custom",
                "severity": custom_finding.get("severity", "Minor"),
                "rule_id": "CUSTOM",
                "rule_name": custom_finding.get("rule", "Custom Rule"),
                "message": custom_finding.get("message", ""),
                "description": "User-defined custom rule violation",
                "recommendation": "Review custom rule configuration",
                "impact": "Custom",
                "effort": "Medium"
            })

    # Step 3: AI-powered code review (optional enhancement)
    ai_result = {}
    try:
        review_metrics = {
            "nesting_depth": workflow.nesting_depth,
            "activity_count": workflow.activity_count,
            "variable_count": workflow.variable_count,
            "complexity_score": workflow.complexity_score,
            "overall_score": overall_score,
            "grade": quality_grade,
        }
        
        # Convert findings to dict format
        findings_dict = [
            {
                "category": f.category if hasattr(f, 'category') else f.get('category'),
                "severity": f.severity if hasattr(f, 'severity') else f.get('severity'),
                "message": f.message if hasattr(f, 'message') else f.get('message'),
                "recommendation": f.recommendation if hasattr(f, 'recommendation') else f.get('recommendation')
            }
            for f in findings
        ]
        
        ai_result = run_code_review_llm(
            workflow_metrics=review_metrics,
            existing_findings=findings_dict,
            db=db,
            user_id=user.user_id
        )
    except Exception as e:
        print(f"AI code review failed: {e}")
        ai_result = {
            "ai_issues": None,
            "ai_best_practices": None,
            "ai_security_concerns": None,
            "ai_refactoring_suggestions": None,
        }

    # Step 4: Create code review record with comprehensive results
    # Convert findings to dict format for JSON storage
    findings_for_db = []
    for f in findings:
        if hasattr(f, '__dict__'):
            finding_dict = {
                "category": f.category,
                "severity": f.severity,
                "rule_id": f.rule_id,
                "rule_name": f.rule_name,
                "message": f.message,
                "description": f.description,
                "recommendation": f.recommendation,
                "activity_name": f.activity_name,
                "impact": f.impact,
                "effort": f.effort
            }
        else:
            finding_dict = f
        findings_for_db.append(finding_dict)

    review = CodeReview(
        workflow_id=workflow.workflow_id,
        overall_score=int(overall_score),
        grade=quality_grade,
        total_issues=len(findings),
        findings=findings_for_db,
        ai_issues=ai_result.get("ai_issues"),
        ai_best_practices=ai_result.get("ai_best_practices"),
        ai_security_concerns=ai_result.get("ai_security_concerns"),
        ai_refactoring_suggestions=ai_result.get("ai_refactoring_suggestions"),
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    # Return combined results
    severity_counts = get_severity_counts([f for f in findings if hasattr(f, 'severity')])
    
    return {
        "review_id": str(review.review_id),
        "overall_score": overall_score,
        "grade": quality_grade,
        "total_issues": len(findings),
        "severity_counts": severity_counts,
        "category_scores": category_scores,
        "findings": findings_for_db,
        "ai_issues": ai_result.get("ai_issues"),
        "ai_best_practices": ai_result.get("ai_best_practices"),
        "ai_security_concerns": ai_result.get("ai_security_concerns"),
        "ai_refactoring_suggestions": ai_result.get("ai_refactoring_suggestions"),
        "cached": False
    }


@router.get("")
def get_review(
    workflow_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get existing code review for a workflow (intelligent caching)"""
    review = db.query(CodeReview).filter(
        CodeReview.workflow_id == workflow_id
    ).first()
    
    if not review:
        return {"message": "No review found for this workflow"}
    
    return {
        "review_id": str(review.review_id),
        "overall_score": review.overall_score,
        "grade": review.grade,
        "total_issues": review.total_issues,
        "findings": review.findings,
        "ai_issues": review.ai_issues,
        "ai_best_practices": review.ai_best_practices,
        "ai_security_concerns": review.ai_security_concerns,
        "ai_refactoring_suggestions": review.ai_refactoring_suggestions,
        "reviewed_at": review.reviewed_at.isoformat() if review.reviewed_at else None,
        "cached": True
    }


@router.get("/{review_id}")
def get_review_by_id(
    review_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """Get specific code review by ID"""
    review = db.query(CodeReview).filter(CodeReview.review_id == review_id).first()
    
    if not review:
        raise HTTPException(status_code=404, detail="Code review not found")
    
    return {
        "review_id": str(review.review_id),
        "workflow_id": str(review.workflow_id),
        "overall_score": review.overall_score,
        "grade": review.grade,
        "total_issues": review.total_issues,
        "findings": review.findings,
        "ai_issues": review.ai_issues,
        "ai_best_practices": review.ai_best_practices,
        "ai_security_concerns": review.ai_security_concerns,
        "ai_refactoring_suggestions": review.ai_refactoring_suggestions,
        "reviewed_at": review.reviewed_at.isoformat() if review.reviewed_at else None
    }

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.workflow import Workflow
from app.models.code_review import CodeReview
from app.services.code_review.engine import run_code_review
from app.services.code_review.code_review_llm_gateway import run_code_review_llm
from app.models.user import User

router = APIRouter(prefix="/api/v1/code-review", tags=["Code Review"])


@router.post("")
def review(
    workflow_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    workflow = db.query(Workflow).filter(Workflow.workflow_id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    metrics = {
        "nesting_depth": workflow.nesting_depth,
        "activity_count": workflow.activity_count,
        "variable_count": workflow.variable_count,
    }

    # Step 1: Rule-based code review
    result = run_code_review(metrics)

    # Step 2: AI-powered code review (with graceful fallback)
    ai_result = {}
    try:
        # Prepare metrics with review results for AI
        review_metrics = {
            **metrics,
            "complexity_score": workflow.complexity_score,
            "overall_score": result["overall_score"],
            "grade": result["grade"],
        }
        
        ai_result = run_code_review_llm(
            workflow_metrics=review_metrics,
            existing_findings=result["findings"],
            db=db,
            user_id=user.user_id
        )
    except Exception as e:
        # Graceful degradation - continue without AI insights
        print(f"AI code review failed: {e}")
        ai_result = {
            "ai_issues": None,
            "ai_best_practices": None,
            "ai_security_concerns": None,
            "ai_refactoring_suggestions": None,
        }

    # Step 3: Create code review record with both rule-based and AI results
    review = CodeReview(
        workflow_id=workflow.workflow_id,
        **result,
        ai_issues=ai_result.get("ai_issues"),
        ai_best_practices=ai_result.get("ai_best_practices"),
        ai_security_concerns=ai_result.get("ai_security_concerns"),
        ai_refactoring_suggestions=ai_result.get("ai_refactoring_suggestions"),
    )

    db.add(review)
    db.commit()

    # Return combined results
    return {
        **result,
        "ai_issues": ai_result.get("ai_issues"),
        "ai_best_practices": ai_result.get("ai_best_practices"),
        "ai_security_concerns": ai_result.get("ai_security_concerns"),
        "ai_refactoring_suggestions": ai_result.get("ai_refactoring_suggestions"),
    }

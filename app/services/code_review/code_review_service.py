from sqlalchemy.orm import Session

from app.domain.rule_contracts import RuleContext, RuleFinding
from app.models.workflow import Workflow
from app.models.code_review import CodeReview
from app.core.usage_tracker import increment_ai_calls


def run_code_review(
    db: Session,
    workflow: Workflow,
    user_id,
) -> CodeReview:
    increment_ai_calls(db, user_id)

    context = RuleContext(
        platform=workflow.platform,
        metrics=workflow,  # Workflow stores deterministic metrics
    )

    findings: list[RuleFinding] = []

    # Built-in rule example
    if workflow.nesting_depth > 4:
        findings.append(
            RuleFinding(
                rule_id="CR-001",
                category="Maintainability",
                severity="Major",
                message="High nesting depth detected",
                recommendation="Refactor into smaller workflows",
                impact="Reduced readability",
                effort="Medium",
            )
        )

    score = max(0, 100 - len(findings) * 5)

    review = CodeReview(
        workflow_id=workflow.workflow_id,
        overall_score=score,
        grade=_grade(score),
        total_issues=len(findings),
        findings=[f.__dict__ for f in findings],
    )

    db.add(review)
    db.commit()
    db.refresh(review)

    return review


def _grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"

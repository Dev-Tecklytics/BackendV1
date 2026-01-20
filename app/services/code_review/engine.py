from .rules.error_handling import MissingTryCatchRule

RULES = [
    MissingTryCatchRule(),
]


def run_code_review(workflow_metrics: dict) -> dict:
    findings = []

    for rule in RULES:
        findings.extend(rule.check(workflow_metrics))

    score = max(0, 100 - len(findings) * 5)

    if score >= 90:
        grade = "A"
    elif score >= 80:
        grade = "B"
    elif score >= 70:
        grade = "C"
    elif score >= 60:
        grade = "D"
    else:
        grade = "F"

    return {
        "overall_score": score,
        "grade": grade,
        "total_issues": len(findings),
        "findings": findings,
    }

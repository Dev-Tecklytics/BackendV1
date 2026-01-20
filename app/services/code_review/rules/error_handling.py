from .base import CodeReviewRule


class MissingTryCatchRule(CodeReviewRule):
    id = "ER-001"
    name = "Missing Try-Catch"
    severity = "Critical"

    def check(self, workflow_data: dict) -> list[dict]:
        if workflow_data["nesting_depth"] > 3:
            return [{
                "rule_id": self.id,
                "message": "High nesting without Try-Catch",
                "severity": self.severity,
                "recommendation": "Wrap main logic in Try-Catch"
            }]
        return []

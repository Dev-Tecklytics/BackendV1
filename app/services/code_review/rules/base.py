from abc import ABC, abstractmethod


class CodeReviewRule(ABC):
    id: str
    name: str
    severity: str  # Critical | Major | Minor | Info

    @abstractmethod
    def check(self, workflow_data: dict) -> list[dict]:
        """
        Return list of findings
        """
        pass

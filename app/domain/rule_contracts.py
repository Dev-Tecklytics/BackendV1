from dataclasses import dataclass
from app.domain.analysis_contracts import DeterministicMetrics


@dataclass
class RuleContext:
    platform: str
    metrics: DeterministicMetrics


@dataclass
class RuleFinding:
    rule_id: str
    category: str
    severity: str # Critical | Major | Minor | Info
    message: str
    recommendation: str
    impact: str
    effort: str

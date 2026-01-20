from dataclasses import dataclass
from app.domain.analysis_contracts import DeterministicMetrics


@dataclass
class LLMInput:
    platform: str
    metrics: DeterministicMetrics
    activity_summary: dict[str, int]


@dataclass
class LLMOutput:
    summary: str
    risks: list[str]
    optimization_suggestions: list[str]
    migration_notes: list[str]

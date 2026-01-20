from typing import Any
from dataclasses import dataclass


@dataclass
class ParsedWorkflow:
    platform: str
    activities: list[str]
    variables: list[str]
    nesting_depth: int
    raw_tree: Any  # lxml root, never persisted


@dataclass
class DeterministicMetrics:
    activity_count: int
    variable_count: int
    nesting_depth: int
    invoked_workflows: int
    has_custom_code: bool


@dataclass
class ComplexityScore:
    score: int
    level: str  # Low | Medium | High | Very High

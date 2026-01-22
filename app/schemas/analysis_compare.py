from pydantic import BaseModel
from typing import Optional, List


class ComparisonMetrics(BaseModel):
    totalActivities: int
    directMappings: int
    incompatibilities: int
    estimatedEffort: int


class ActivityMapping(BaseModel):
    source: str
    target: Optional[str]
    compatible: bool


class PlatformComparisonResponse(BaseModel):
    metrics: ComparisonMetrics
    activityMappings: List[ActivityMapping]
    incompatibilities: List[str]

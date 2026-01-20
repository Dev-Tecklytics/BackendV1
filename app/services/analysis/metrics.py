from collections import Counter
from app.domain.analysis_contracts import ParsedWorkflow, DeterministicMetrics


def calculate_metrics(parsed: ParsedWorkflow) -> DeterministicMetrics:
    invoked_workflows = sum(
        1 for a in parsed.activities if "Invoke" in a
    )

    has_custom_code = any(
        "Code" in a or "Script" in a for a in parsed.activities
    )

    return DeterministicMetrics(
        activity_count=len(parsed.activities),
        variable_count=len(parsed.variables),
        nesting_depth=parsed.nesting_depth,
        invoked_workflows=invoked_workflows,
        has_custom_code=has_custom_code,
    )

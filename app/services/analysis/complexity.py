from app.domain.analysis_contracts import DeterministicMetrics, ComplexityScore


def calculate_complexity(metrics: DeterministicMetrics) -> ComplexityScore:
    score = (
        metrics.activity_count * 1
        + metrics.nesting_depth * 3
        + metrics.variable_count * 1
        + metrics.invoked_workflows * 2
        + (5 if metrics.has_custom_code else 0)
    )

    if score < 20:
        level = "Low"
    elif score < 50:
        level = "Medium"
    elif score < 100:
        level = "High"
    else:
        level = "Very High"

    return ComplexityScore(score=score, level=level)

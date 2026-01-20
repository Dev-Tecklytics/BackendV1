def compare_workflow(activity_count: int, mapped: int):
    score = int((mapped / activity_count) * 100)
    effort = max(1, activity_count - mapped)

    return {
        "compatibility_score": score,
        "migration_effort": effort
    }

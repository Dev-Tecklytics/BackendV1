from app.models.workflow import Workflow
from app.models.activity_mapping import ActivityMapping as MappingModel


def compare_platforms(workflow: Workflow, mappings: list[MappingModel]):
    total = workflow.activity_count
    mapped = len([m for m in mappings if m.compatibility_score >= 80])
    incompatible = total - mapped

    return {
        "metrics": {
            "totalActivities": total,
            "directMappings": mapped,
            "incompatibilities": incompatible,
            "estimatedEffort": incompatible * 2,
        },
        "activityMappings": [
            {
                "source": m.source_activity,
                "target": m.target_activity,
                "compatible": m.compatibility_score >= 80,
            }
            for m in mappings
        ],
        "incompatibilities": [
            m.source_activity
            for m in mappings
            if m.compatibility_score < 80
        ],
    }

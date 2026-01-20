from sqlalchemy.orm import Session

from app.services.analysis.parser import parse_workflow
from app.services.analysis.metrics import calculate_metrics
from app.services.analysis.complexity import calculate_complexity
from app.services.analysis.llm_gateway import run_llm_analysis

from app.domain.llm_contracts import LLMInput
from app.models.workflow import Workflow
from app.models.file import File


def run_analysis(
    db: Session,
    file: File,
    platform: str,
    user_id=None,  # Optional for backward compatibility
) -> Workflow:
    # 1. Parse
    parsed = parse_workflow(file.file_path, platform)

    # 2. Metrics
    metrics = calculate_metrics(parsed)

    # 3. Complexity
    complexity = calculate_complexity(metrics)

    # 4. LLM (augmentation only) - only if user_id provided
    if user_id:
        llm_input = LLMInput(
            platform=platform,
            metrics=metrics,
            activity_summary={},
        )
        llm_output = run_llm_analysis(llm_input, db, user_id)

    # 5. Persist
    workflow = Workflow(
        project_id=file.project_id,
        file_id=file.file_id,
        platform=platform,
        activity_count=metrics.activity_count,
        variable_count=metrics.variable_count,
        nesting_depth=metrics.nesting_depth,
        complexity_score=complexity.score,
        complexity_level=complexity.level,
        # LLM fields can be added later to model
    )

    db.add(workflow)
    db.commit()
    db.refresh(workflow)

    return workflow

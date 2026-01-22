import time
import logging
from pathlib import Path
from sqlalchemy.orm import Session
from app.models.analysis_history import AnalysisHistory, AnalysisStatus
from app.core.database import SessionLocal
from app.services.analysis.parser import parse_workflow
from app.services.analysis.metrics import calculate_metrics
from app.services.analysis.llm_gateway import run_llm_analysis
from app.domain.llm_contracts import LLMInput

logger = logging.getLogger(__name__)

def process_analysis_async(analysis_id: str):
    db: Session = SessionLocal()
    analysis = None

    try:
        analysis = (
            db.query(AnalysisHistory)
            .filter(AnalysisHistory.analysis_id == analysis_id)
            .first()
        )

        if not analysis:
            logger.warning(f"Analysis {analysis_id} not found")
            return

        # Update status to processing
        analysis.status = AnalysisStatus.IN_PROGRESS
        db.commit()
        logger.info(f"Analysis {analysis_id} started processing")

        # Check if file exists
        if not analysis.file_path or not Path(analysis.file_path).exists():
            raise FileNotFoundError(f"File not found: {analysis.file_path}")

        # Detect platform from file extension
        file_ext = Path(analysis.file_name).suffix.lower()
        if file_ext == ".xaml":
            platform = "UiPath"
        elif file_ext == ".atmx":
            platform = "Automation Anywhere"
        else:
            platform = "Unknown"

        # Parse the workflow file
        logger.info(f"Parsing workflow file: {analysis.file_path}")
        parsed_workflow = parse_workflow(analysis.file_path, platform)

        # Calculate metrics
        logger.info(f"Calculating metrics for {analysis_id}")
        metrics = calculate_metrics(parsed_workflow)

        # Prepare LLM input
        llm_input = LLMInput(
            platform=platform,
            metrics=metrics,
            activity_summary={}  # Can be enhanced later
        )

        # Call LLM for analysis
        logger.info(f"Calling LLM for analysis {analysis_id}")
        llm_output = run_llm_analysis(llm_input, db, analysis.user_id, file_path=analysis.file_path)

        # Store results
        analysis.result = {
            "platform": platform,
            "metrics": {
                "activity_count": metrics.activity_count,
                "variable_count": metrics.variable_count,
                "nesting_depth": metrics.nesting_depth,
                "invoked_workflows": metrics.invoked_workflows,
                "has_custom_code": metrics.has_custom_code
            },
            "summary": llm_output.summary,
            "risks": llm_output.risks,
            "optimization_suggestions": llm_output.optimization_suggestions,
            "migration_notes": llm_output.migration_notes
        }

        analysis.status = AnalysisStatus.COMPLETED
        db.commit()
        logger.info(f"Analysis {analysis_id} completed successfully")

    except Exception as e:
        logger.error(f"Analysis {analysis_id} failed with error: {str(e)}", exc_info=True)
        if analysis:
            analysis.status = AnalysisStatus.FAILED
            analysis.result = {
                "error": str(e),
                "error_type": type(e).__name__
            }
            db.commit()
    finally:
        db.close()

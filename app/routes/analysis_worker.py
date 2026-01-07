import time
from app.core.database import SessionLocal
from app.models.analysis_history import AnalysisHistory

def process_analysis(analysis_id, file_name):
    db = SessionLocal()
    try:
        analysis = (
            db.query(AnalysisHistory)
            .filter(AnalysisHistory.analysis_id == analysis_id)
            .first()
        )

        if not analysis:
            return

        # Mark as processing
        analysis.status = "processing"
        db.commit()

        # Simulate heavy work
        time.sleep(5)

        # Fake analysis result
        analysis.status = "completed"
        analysis.result = f"Analysis completed for {file_name}"
        db.commit()

    except Exception as e:
        analysis.status = "failed"
        analysis.result = str(e)
        db.commit()
    finally:
        db.close()

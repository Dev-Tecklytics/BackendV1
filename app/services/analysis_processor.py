import time
from sqlalchemy.orm import Session
from app.models.analysis_history import AnalysisHistory, AnalysisStatus
from app.core.database import SessionLocal

def process_analysis_async(analysis_id: str):
    db: Session = SessionLocal()

    try:
        analysis = (
            db.query(AnalysisHistory)
            .filter(AnalysisHistory.analysis_id == analysis_id)
            .first()
        )

        if not analysis:
            return

        analysis.status = AnalysisStatus.PROCESSING
        db.commit()

        # Simulate heavy analysis
        time.sleep(10)

        analysis.status = AnalysisStatus.COMPLETED
        db.commit()

    except Exception:
        analysis.status = AnalysisStatus.FAILED
        db.commit()
    finally:
        db.close()

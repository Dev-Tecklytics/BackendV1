import csv
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.workflow import Workflow

router = APIRouter(prefix="/api/v1/export", tags=["Export"])


@router.get("/csv")
def export_csv(db: Session = Depends(get_db)):
    def generate():
        yield "workflow_id,score,level\n"
        for w in db.query(Workflow).all():
            yield f"{w.workflow_id},{w.complexity_score},{w.complexity_level}\n"

    return StreamingResponse(generate(), media_type="text/csv")

import os
import shutil
from fastapi import APIRouter, UploadFile, File as UploadFileType, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.file import File
from app.models.user import User

UPLOAD_ROOT = "data/uploads"

router = APIRouter(prefix="/api/v1/files", tags=["Files"])


@router.post("/upload")
def upload_file(
    project_id: UUID,
    upload: UploadFile = UploadFileType(...),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    os.makedirs(f"{UPLOAD_ROOT}/{project_id}", exist_ok=True)

    file_path = f"{UPLOAD_ROOT}/{project_id}/{upload.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload.file, buffer)

    db_file = File(
        project_id=project_id,
        file_name=upload.filename,
        file_path=file_path,
        file_size=os.path.getsize(file_path),
    )

    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    return {"file_id": db_file.file_id, "file_name": db_file.file_name}

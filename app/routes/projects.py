from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectOut
from app.services.projects import project_service

router = APIRouter(prefix="/api/v1/projects", tags=["Projects"])


@router.post("", response_model=ProjectOut)
def create(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return project_service.create_project(db, user.user_id, data)


@router.get("", response_model=list[ProjectOut])
def list_all(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return project_service.list_projects(db, user.user_id)


@router.get("/{project_id}", response_model=ProjectOut)
def get_one(
    project_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    project = project_service.get_project(db, project_id, user.user_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.patch("/{project_id}", response_model=ProjectOut)
def update(
    project_id: UUID,
    data: ProjectUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    project = project_service.get_project(db, project_id, user.user_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project_service.update_project(db, project, data)


@router.delete("/{project_id}")
def delete(
    project_id: UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    project = project_service.get_project(db, project_id, user.user_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project_service.delete_project(db, project)
    
    return {
        "message": "Project deleted successfully",
        "project_id": str(project_id)
    }


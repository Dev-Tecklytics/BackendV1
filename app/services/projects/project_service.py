from sqlalchemy.orm import Session
from uuid import UUID

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate


def get_project_by_name(db: Session, user_id: UUID, name: str) -> Project | None:
    """Get a project by name for a specific user."""
    return (
        db.query(Project)
        .filter(Project.user_id == user_id, Project.name == name)
        .first()
    )


def create_project(db: Session, user_id: UUID, data: ProjectCreate) -> Project:
    # Check if project with same name already exists for this user
    existing_project = get_project_by_name(db, user_id, data.name)
    if existing_project:
        # Return existing project instead of creating duplicate
        return existing_project
    
    # Create new project
    project = Project(
        user_id=user_id,
        name=data.name,
        platform=data.platform,
        description=data.description,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def list_projects(db: Session, user_id: UUID) -> list[Project]:
    return db.query(Project).filter(Project.user_id == user_id).all()


def get_project(db: Session, project_id: UUID, user_id: UUID) -> Project | None:
    return (
        db.query(Project)
        .filter(Project.project_id == project_id, Project.user_id == user_id)
        .first()
    )


def update_project(
    db: Session, project: Project, data: ProjectUpdate
) -> Project:
    if data.name is not None:
        project.name = data.name
    if data.description is not None:
        project.description = data.description

    db.commit()
    db.refresh(project)
    return project


def delete_project(db: Session, project: Project):
    # Manually delete related records to avoid foreign key violations 
    # if DB constraints don't have CASCADE set up.
    from app.models.workflow import Workflow
    from app.models.file import File
    from app.models.code_review import CodeReview
    
    # Get all workflow IDs for this project to clean up their reviews
    workflow_ids = [w.workflow_id for w in db.query(Workflow.workflow_id).filter(Workflow.project_id == project.project_id).all()]
    if workflow_ids:
        db.query(CodeReview).filter(CodeReview.workflow_id.in_(workflow_ids)).delete(synchronize_session=False)

    db.query(Workflow).filter(Workflow.project_id == project.project_id).delete(synchronize_session=False)
    db.query(File).filter(File.project_id == project.project_id).delete(synchronize_session=False)
    
    db.delete(project)
    db.commit()

from pydantic import BaseModel
from uuid import UUID
from datetime import datetime


class ProjectCreate(BaseModel):
    name: str
    platform: str
    description: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class ProjectOut(BaseModel):
    project_id: UUID
    name: str
    platform: str
    description: str | None
    created_at: datetime

    class Config:
        from_attributes = True

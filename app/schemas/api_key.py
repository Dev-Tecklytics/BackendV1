from uuid import UUID
from pydantic import BaseModel
from datetime import datetime

class ApiKeyCreateResponse(BaseModel):
    api_key: str
    name: str | None = None


class ApiKeyListResponse(BaseModel):
    api_key_id: UUID
    name: str | None
    key_prefix: str
    created_at: datetime
    is_active: bool

    class Config:
        from_attributes = True
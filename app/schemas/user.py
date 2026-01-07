from uuid import UUID
from pydantic import BaseModel, EmailStr

class UserRegistrationRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None
    company_name: str | None = None

class UserResponse(BaseModel):
    user_id: UUID
    email: EmailStr
    full_name: str | None = None

    class Config:
        from_attributes = True
from fastapi import APIRouter, Depends
from app.core.auth import get_current_user
from app.models.user import User
from app.core.deps import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/user", tags=["User"])

# Example
@router.get("/me")
def get_profile(current_user: User = Depends(get_current_user)):
    return {
        "user_id": str(current_user.user_id),
        "email": current_user.email,
        "full_name": current_user.full_name,
    }

@router.put("/profile")
def update_profile(
    full_name: str | None = None,
    company_name: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    current_user.full_name = full_name
    current_user.company_name = company_name
    db.commit()
    return {"message": "Profile updated"}
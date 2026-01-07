from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.core.admin_auth import require_admin
from app.models.user import User

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["Admin APIs"]
)

@router.get("/users")
def list_users(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_admin)
):
    users = db.query(User).order_by(User.created_at.desc()).all()

    return [
        {
            "user_id": str(user.user_id),
            "email": user.email,
            "full_name": user.full_name,
            "company_name": user.company_name,
            "role": user.role.value,
            "status": user.status.value,
            "created_at": user.created_at
        }
        for user in users
    ]


from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.admin_auth import require_admin
from app.core.deps import get_db
from app.models.api_key import ApiKey

router = APIRouter(
    prefix="/api/v1/admin/api-keys",
    tags=["Admin APIs"]
)

@router.get("")
def list_api_keys(
    db: Session = Depends(get_db),
    admin = Depends(require_admin)
):
    return db.query(ApiKey).all()

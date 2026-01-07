from fastapi import APIRouter, Depends, HTTPException, status   
from sqlalchemy.orm import Session
from app.core.deps import get_db
from app.core.auth import get_current_user
from app.core.api_key import generate_api_key
from app.models.api_key import ApiKey
from app.schemas.api_key import ApiKeyCreateResponse, ApiKeyListResponse
from app.models.user import User

router = APIRouter(prefix="/api/v1/api_key", tags=["API Key"])

# Create APi Key
@router.post("", response_model=ApiKeyCreateResponse)
def create_api_key(
    name: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    raw_key, prefix, key_hash = generate_api_key()
    api_key = ApiKey(
        user_id=current_user.user_id,
        key_hash=key_hash,
        name=name,
        key_prefix=prefix
    )

    # Adding to DB
    db.add(api_key)
    db.commit()
    db.refresh(api_key)

    return {"api_key": raw_key, "name": name}

# List API Key
@router.get("", response_model=list[ApiKeyListResponse])
def list_api_key(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return (
        db.query(ApiKey)
        .filter(ApiKey.user_id == current_user.user_id)
        .all()
    )

# Delete API key
@router.delete("/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_api_key(
    api_key_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    api_key = (
    db.query(ApiKey)
    .filter(ApiKey.api_key_id == api_key_id)
    .filter(ApiKey.is_active == True)
    .first()
)


    if not api_key:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API key not found")

    api_key.is_active = False
    db.commit()


@router.put("/{api_key_id}/rotate")
def rotate_api_key(
    api_key_id: str,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    raw_key, prefix, key_hash = generate_api_key()

    api_key = db.query(ApiKey).filter(
        ApiKey.api_key_id == api_key_id,
        ApiKey.user_id == current_user.user_id
    ).first()

    api_key.key_hash = key_hash
    api_key.key_prefix = prefix
    db.commit()

    return {"new_api_key": raw_key}
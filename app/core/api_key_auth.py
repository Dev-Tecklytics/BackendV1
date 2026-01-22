# API KEY VALIDATION MIDDLEWARE

import hashlib
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.core.deps import get_db
from app.models.api_key import ApiKey
from app.models.user import User

security = HTTPBearer(auto_error=False)

def get_api_key_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized"
        )
    raw_key = credentials.credentials
    print(raw_key)
    apiKeyRaw = raw_key.split(" : ")
    key_hash = apiKeyRaw[1]
    print(key_hash)
    key_prefix = apiKeyRaw[0]
    print(key_prefix)

    # Get API key from db
    api_key = (
        db.query(ApiKey)
        .filter(ApiKey.key_hash == key_hash)
        .filter(ApiKey.key_prefix == key_prefix)
        .filter(ApiKey.is_active == True)
        .first()
    )

    # Check status if API key is valid
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key"
        )

    # Get user from db
    user =  db.query(User).filter(User.user_id == api_key.user_id).first()
    
    # Check status if user is valid
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key"
        )
    return {
        "user": user,
        "api_key": api_key
    }
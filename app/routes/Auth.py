from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import logging

# Standard imports matching your project structure
try:
    from app.schemas.user import UserRegistrationRequest, UserResponse
    from app.models.user import User
    from app.core.deps import get_db
    from app.core.security import hash_password, verify_password
    from app.schemas.auth import LoginRequest, TokenResponse
    from app.core.jwt import create_access_token
    from app.core.auth import get_current_user
except ImportError as e:
    logging.error(f"IMPORT ERROR: {e}")
    raise

# Setup logging to see errors in the terminal
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])

@router.post("/register", response_model=UserResponse)
def register_user(request: UserRegistrationRequest, db: Session = Depends(get_db)):
    logger.info(f"Attempting registration for email: {request.email}")
    try:
        # 1. Checking if user already exists
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            logger.warning(f"Registration failed: Email {request.email} already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # 2. Creating user
        user = User(
            email=request.email,
            password_hash=hash_password(request.password),
            full_name=request.full_name,
            company_name=getattr(request, 'company_name', None) # Safely get company name
        )

        # 3. Saving to DB
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"User created successfully: {user.email}")
        return user
    except Exception as e:
        logger.error(f"DATABASE ERROR during registration: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

@router.post("/login") # Removed TokenResponse schema temporarily to avoid 500 validation errors
def login(request: LoginRequest, db: Session = Depends(get_db)):
    logger.info(f"Login attempt for: {request.email}")
    try:
        user = db.query(User).filter(User.email == request.email).first()
        if not user:
            logger.warning(f"Login failed: User {request.email} not found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        if not verify_password(request.password, user.password_hash):
            logger.warning(f"Login failed: Wrong password for {request.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        token = create_access_token({"sub": str(user.user_id)})
        logger.info(f"Login successful for: {request.email}")
        
        # Return a structure that satisfies most JWT frontends
        return {
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "email": user.email,
                "full_name": user.full_name,
                "user_id": user.user_id
            }
        }
    except Exception as e:
        logger.error(f"LOGIN ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/refresh-token")
def refresh_token(current_user=Depends(get_current_user)):
    try:
        token = create_access_token({"sub": str(current_user.user_id)})
        return {
            "access_token": token,
            "token_type": "bearer"
        }
    except Exception as e:
        logger.error(f"REFRESH ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout():
    return None

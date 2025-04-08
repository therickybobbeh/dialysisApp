from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from jose import jwt, JWTError

from app.db.schemas.user import UserCreate, UserResponse
from app.db.models.user import User
from app.core.security import create_access_token, verify_password, hash_password, create_refresh_token
from app.db.session import get_db
from app.core.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter()


# **Register User API**
@router.post("/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        hashed_password = hash_password(user.password)
        db_user = User(name=user.name, email=user.email, password=hashed_password, role=user.role)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as e:
        logger.error(f"Error during registration: {e}")
        raise HTTPException(status_code=400, detail="Registration failed")


#  **Login API (Returns Access & Refresh Tokens)**
@router.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """ Authenticate user and generate access + refresh tokens """

    logger.debug(f" Login attempt: {form_data.username}")

    user = db.query(User).filter(User.email == form_data.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    #  Generate Tokens todo MAYBE not needed to return here
    token_data = {
        "sub": user.email,
        "user_id": user.id,
        "role": user.role
    }

    if user.role == "provider":
        token_data["patients"] = user.patients

    access_token = create_access_token(token_data, timedelta(minutes=30))
    refresh_token = create_refresh_token(token_data)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


#  **Refresh Access Token API**
@router.post("/refresh")
def refresh_access_token(refresh_token: str, db: Session = Depends(get_db)):
    """ Generate a new access token using a valid refresh token """
    try:
        payload = jwt.decode(refresh_token, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("user_id")

        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        new_access_token = create_access_token(
            {"sub": user.email, "user_id": user.id, "role": user.role},
            timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        return {"access_token": new_access_token}
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

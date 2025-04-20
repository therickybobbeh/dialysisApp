from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError

from app.db.fhir_integration import fhir_create_patient_resource
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
    # 1) Check if email is already taken
    existing = db.query(User).filter(User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 2) Hash and persist the user
    try:
        hashed_password = hash_password(user.password)
        db_user = User(
            name=user.name,
            email=user.email,
            password=hashed_password,
            role=user.role,
            height=user.height,
            sex=user.sex,
            notifications={
                "protein": False,
                "effluentVolume": False,
                "lowBloodPressure": False,
                "fluidOverloadHigh": False,
                "highBloodPressure": False,
                "fluidOverloadWatch": False,
                "dialysisGrowthAdjustment": False
            },
            birth_date=user.birth_date,
        )
        db.add(db_user)
        # TODO: add logic to pick providers
        doctor_email = "drsmith@example.com"
        doctor = db.query(User).filter(User.email == doctor_email).first()

        if doctor:
            if doctor.patients is None:
                doctor.patients = set()
            else:
                doctor.patients = set(doctor.patients)
            doctor.patients.add(db_user.id)
            db.commit()
            logger.info(f"Added patient {db_user.id} to Dr. {doctor.name}'s patient list.")

        db.commit()
        db.refresh(db_user)
    except Exception as db_err:
        logger.error(f"DB error during registration: {db_err}")
        raise HTTPException(status_code=500, detail="Failed to save user to database")

    # 3) Try to create the FHIR resource
    try:
        import asyncio
        asyncio.run(fhir_create_patient_resource(
            patient_id=db_user.id,
            name=db_user.name,
            birth_date=user.birth_date,
            gender=db_user.sex,
            height=db_user.height
        ))
    except Exception as fhir_err:
        logger.error(f"User saved in DB, but FHIR creation failed: {fhir_err}")
        # Return 201 but include info about FHIR failure
        raise HTTPException(
            status_code=201,
            detail="User registered, but failed to create FHIR resource"
        )

    # 4) All good
    return db_user

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

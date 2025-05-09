from fastapi import HTTPException, status, Security, Depends, Query
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from argon2 import PasswordHasher
from app.core.config import settings
from app.db.session import get_db
from app.db.models.user import User
from sqlalchemy.orm import Session
from app.core.logging_config import logger
from datetime import datetime, timedelta
from typing import Optional, Tuple, Annotated
from argon2.exceptions import VerifyMismatchError

# Initialize Argon2 Password Hasher
ph = PasswordHasher()

# OAuth2 Token Scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_current_user(token: str = Security(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    Verify Access Token & Retrieve User.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        role: str = payload.get("role")  # Extract role

        logger.info(f"Decoded Token -> Email: {email}, ID: {user_id}, Role: {role}")

        if email is None or user_id is None or role not in ["patient", "provider"]:
            logger.error("Invalid user or missing role")
            raise credentials_exception

        user = db.query(User).filter(User.id == user_id, User.email == email).first()
        if user is None:
            logger.error("User not found in database")
            raise credentials_exception

        return user
    except JWTError as e:
        logger.error(f"JWT validation error: {str(e)}")
        raise credentials_exception


def get_current_user_with_optional_patient(
        token: str = Security(oauth2_scheme),
        patient_primary_id: Optional[int] = Query(None, description="Optional patient primary ID"),
        db: Session = Depends(get_db)
        ) -> Tuple[User, Optional[int]]:
    """
    This dependency returns a tuple: the current user and an optional patient_primary_id.
    - Providers may supply a patient_primary_id to query a specific patient.
    - Patients must not supply an ID other than their own.
    """
    user = get_current_user(token, db)

    if patient_primary_id is not None:
        if user.role == "provider":
            # Provider may query based on provided patient_primary_id.
            return user, patient_primary_id
        elif user.role == "patient":
            # A patient can only query their own data.
            if user.id != patient_primary_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Patients can only query their own data"
                )
    return user, None


# Create JWT Access Token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (
        expires_delta if expires_delta else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# Create JWT Refresh Token
def create_refresh_token(data: dict, expires_delta: timedelta = timedelta(days=7)):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.REFRESH_SECRET_KEY, algorithm=settings.ALGORITHM)


# Hash password using Argon2
def hash_password(password: str) -> str:
    return ph.hash(password)


# Verify password using Argon2
def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return ph.verify(hashed_password.strip(), plain_password)
    except VerifyMismatchError:
        logger.warning("Password verification failed: Incorrect password.")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during password verification: {str(e)}")
        return False


# Decode & Verify JWT Token
def verify_jwt_token(token: str, secret_key: str):
    try:
        return jwt.decode(token, secret_key, algorithms=[settings.ALGORITHM])
    except JWTError as e:
        logger.error(f"JWT validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid token",
        )


class RoleChecker:
    def __init__(self, allowed_roles):
        self.allowed_roles = allowed_roles

    def __call__(self, user: Annotated[User, Depends(get_current_user)]):
        if user.role in self.allowed_roles:
            return True
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="You don't have enough permissions"
        )

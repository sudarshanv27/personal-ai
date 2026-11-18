from datetime import datetime, timedelta, timezone
import hashlib
import secrets

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session as DBSession

from app.core.permissions import require_owner
from app.core.config import settings
from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.database.connection import get_db
from app.models.session import Session
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    LogoutResponse,
    RefreshRequest,
    RefreshResponse,
    RegisterRequest,
    UserResponse,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# ============================================================
# REFRESH TOKEN HASH
# ============================================================

def hash_token(token: str) -> str:
    return hashlib.sha256(
        token.encode()
    ).hexdigest()


# ============================================================
# REGISTER
# ============================================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: RegisterRequest,
    db: DBSession = Depends(get_db),
):

    existing_email = db.scalar(
        select(User).where(
            User.email == payload.email
        )
    )

    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    existing_username = db.scalar(
        select(User).where(
            User.username == payload.username
        )
    )

    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists",
        )

    user = User(
        username=payload.username,
        email=payload.email,
        password_hash=hash_password(
            payload.password
        ),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


# ============================================================
# LOGIN
# ============================================================

@router.post(
    "/login",
    response_model=LoginResponse,
)
def login(
    payload: LoginRequest,
    db: DBSession = Depends(get_db),
):

    user = db.scalar(
        select(User).where(
            User.email == payload.email
        )
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    if not verify_password(
        payload.password,
        user.password_hash,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(
        user.id,
        settings.jwt_access_token_expire_minutes,
    )

    refresh_token = secrets.token_urlsafe(48)

    expires_at = (
        datetime.now(timezone.utc)
        + timedelta(days=7)
    )

    session = Session(
        user_id=user.id,
        token_hash=hash_token(
            refresh_token
        ),
        expires_at=expires_at,
    )

    db.add(session)
    db.commit()

    return LoginResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        user=user,
    )


# ============================================================
# CURRENT USER
# ============================================================

@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(
        require_owner
    ),
):
    return current_user


# ============================================================
# REFRESH ACCESS TOKEN
# ============================================================

@router.post(
    "/refresh",
    response_model=RefreshResponse,
)
def refresh_access_token(
    payload: RefreshRequest,
    db: DBSession = Depends(get_db),
):
    # Hash the supplied refresh token
    token_hash = hash_token(
        payload.refresh_token
    )

    # Find the session
    session = db.scalar(
        select(Session).where(
            Session.token_hash == token_hash
        )
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Check expiration
    if session.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token expired",
        )

    # Find associated user
    user = db.scalar(
        select(User).where(
            User.id == session.user_id
        )
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Check account status
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # Create a new access token
    access_token = create_access_token(
        user.id,
        settings.jwt_access_token_expire_minutes,
    )

    return RefreshResponse(
        access_token=access_token,
        token_type="bearer",
    )

# ============================================================
# LOGOUT
# ============================================================

@router.post(
    "/logout",
    response_model=LogoutResponse,
)
def logout(
    payload: LogoutRequest,
    db: DBSession = Depends(get_db),
):
    token_hash = hash_token(
        payload.refresh_token
    )

    session = db.scalar(
        select(Session).where(
            Session.token_hash == token_hash
        )
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    db.delete(session)
    db.commit()

    return LogoutResponse(
        message="Logged out successfully"
    )
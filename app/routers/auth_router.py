"""
auth_router.py - Authentication Endpoints
Register, Login, and current user info
"""

from fastapi import APIRouter, HTTPException, Depends, status
from app.schemas import UserRegister, UserResponse, Token, UserLogin
from app.models import User, UserRole, fake_users_db
from app.auth import (
    hash_password,
    authenticate_user,
    create_access_token,
    get_current_user
)
import structlog

logger = structlog.get_logger("app.auth_router")

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(user_data: UserRegister):
    if user_data.username in fake_users_db:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    user = User(
        id=len(fake_users_db) + 1,
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role=user_data.role
    )

    fake_users_db[user_data.username] = user

    logger.info(
        "user_registered",
        username=user.username,
        role=user.role.value,
        user_id=user.id
    )

    return user


@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    user = authenticate_user(user_data.username, user_data.password)

    if not user:
        logger.warning(
            "failed_login_attempt",
            username=user_data.username
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={
        "sub": user.username,
        "role": user.role.value
    })

    logger.info(
        "user_logged_in",
        username=user.username,
        role=user.role.value
    )

    return Token(access_token=access_token)


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    logger.info("user_accessed_profile", username=current_user.username)
    return current_user

@router.get("/debug/users", include_in_schema=False)
async def debug_users():
    return {
        username: {
            "id": user.id,
            "email": user.email,
            "role": user.role.value,
            "is_active": user.is_active
        }
        for username, user in fake_users_db.items()
    }
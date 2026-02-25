"""
users_router.py - User Management Endpoints
Demonstrates RBAC in action
"""

from fastapi import APIRouter, Depends
from app.models import User, fake_users_db
from app.schemas import UserResponse
from app.dependencies import require_admin, require_moderator, require_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
async def get_my_profile(current_user: User = Depends(require_user)):
    return current_user


@router.get("/all", response_model=list[UserResponse])
async def get_all_users(current_user: User = Depends(require_moderator)):
    return list(fake_users_db.values())


@router.delete("/{username}")
async def delete_user(
    username: str,
    current_user: User = Depends(require_admin)
):
    if username not in fake_users_db:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    del fake_users_db[username]
    return {"message": f"User {username} deleted"}
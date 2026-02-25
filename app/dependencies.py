"""
dependencies.py - Reusable FastAPI Dependencies
RBAC role checking and other shared dependencies
"""

from fastapi import Depends, HTTPException, status
from app.models import User, UserRole
from app.auth import get_current_user


def require_role(*allowed_roles: UserRole):
    async def role_checker(
        current_user: User = Depends(get_current_user)
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in allowed_roles]}"
            )
        return current_user
    return role_checker


require_admin = require_role(UserRole.ADMIN)
require_moderator = require_role(UserRole.MODERATOR, UserRole.ADMIN)
require_user = require_role(UserRole.USER, UserRole.MODERATOR, UserRole.ADMIN)
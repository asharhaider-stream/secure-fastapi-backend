"""
schemas.py - API Boundary Data Validation
"""

from pydantic import BaseModel, EmailStr
from app.models import UserRole


class UserRegister(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.USER


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRole
    is_active: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: str | None = None
    role: UserRole | None = None


class UserLogin(BaseModel):
    username: str
    password: str
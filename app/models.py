"""
models.py - Data Models representing our database structure
"""

from enum import Enum
from dataclasses import dataclass


class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"


@dataclass
class User:
    id: int
    username: str
    email: str
    hashed_password: str
    role: UserRole
    is_active: bool = True


# Temporary in-memory database — replaced with real DB in later steps
fake_users_db: dict = {}
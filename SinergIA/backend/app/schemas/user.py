from sqlmodel import SQLModel
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum
from app.models.user import UserRole

class UserBase(SQLModel):
    username: str
    email: str
    role: UserRole = UserRole.RESEARCHER
    author_id: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    created_at: datetime

class UserUpdate(SQLModel):
    email: Optional[str] = None
    password: Optional[str] = None
    author_id: Optional[str] = None

# Logs de actividad
class UserLogRead(SQLModel):
    id: int
    action: str
    target_entity: Optional[str]
    details: Optional[Any]
    created_at: datetime

from sqlmodel import SQLModel, Field
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum
from app.models.user import UserRole

class UserBase(SQLModel):
    username: str = Field(max_length=150)
    email: str = Field(max_length=254)
    role: UserRole = UserRole.RESEARCHER
    author_id: Optional[str] = Field(default=None, max_length=255)

class UserCreate(UserBase):
    password: str = Field(max_length=255)

class UserRead(UserBase):
    id: int
    created_at: datetime

class UserUpdate(SQLModel):
    email: Optional[str] = Field(default=None, max_length=254)
    password: Optional[str] = Field(default=None, max_length=255)
    author_id: Optional[str] = Field(default=None, max_length=255)

# Activity logs
class UserLogRead(SQLModel):
    id: int
    action: str = Field(max_length=100)
    target_entity: Optional[str] = Field(default=None, max_length=100)
    details: Optional[Any]
    ip_address: Optional[str] = Field(default=None, max_length=45)
    created_at: datetime

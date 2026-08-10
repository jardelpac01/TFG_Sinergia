from typing import Optional, Any, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    RESEARCHER = "researcher"

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, max_length=150)
    email: str = Field(unique=True, max_length=254)
    password_hash: str = Field(max_length=255)
    role: str = Field(
        default=UserRole.RESEARCHER.value,
        max_length=20,
        sa_column_kwargs={"server_default": "researcher"},
    )

    author_id: Optional[str] = Field(default=None, foreign_key="authors.id", max_length=255)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    logs: List["UserLog"] = Relationship(back_populates="user")
    author: Optional["Author"] = Relationship(back_populates="user")
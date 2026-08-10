from typing import Optional, Any, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone

from .user import User

class UserLog(SQLModel, table=True):
    __tablename__ = "user_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    action: str = Field(max_length=100)
    target_entity: Optional[str] = Field(default=None, max_length=100)
    details: Any = Field(default=None, sa_column=Column(JSONB))
    ip_address: Optional[str] = Field(default=None, max_length=45)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: Optional["User"] = Relationship(back_populates="logs")
from datetime import datetime
from typing import Any, Optional

from sqlmodel import SQLModel


class UserLogBase(SQLModel):
    user_id: Optional[int] = None
    action: str
    target_entity: Optional[str] = None
    details: Optional[Any] = None
    ip_address: Optional[str] = None


class UserLogCreate(UserLogBase):
    pass


class UserLogRead(UserLogBase):
    id: int
    created_at: datetime

from typing import Optional, Any, List
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone

class Source(SQLModel, table=True):
    __tablename__ = "sources"

    id: str = Field(primary_key=True)
    display_name: str
    issn: Optional[str] = None
    publisher: Optional[str] = None
    type: Optional[str] = None
    country_code: Optional[str] = Field(default=None, max_length=2)
    is_oa: Optional[bool] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_data: Any = Field(default=None, sa_column=Column(JSONB))

    works: List["Work"] = Relationship(back_populates="source")
from typing import Optional, List, Any
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone

class Institution(SQLModel, table=True):
    __tablename__ = "institutions"

    id: str = Field(primary_key=True)
    name: str
    country_code: Optional[str] = Field(default=None, max_length=2)
    ror: Optional[str] = None
    type: Optional[str] = None
    geo_lat: Optional[float] = None
    geo_lon: Optional[float] = None
    city: Optional[str] = None
    homepage_url: Optional[str] = None
    aliases: Any = Field(default=None, sa_column=Column(JSONB))
    works_count: int = Field(default=0)
    cited_by_count: int = Field(default=0)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_data: Any = Field(default=None, sa_column=Column(JSONB))

    authors: List["Author"] = Relationship(back_populates="last_known_institution")
from typing import Optional, List, Any
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from datetime import date, datetime, timezone
from .author_work import AuthorWork
from .work_topic import WorkTopic

class Work(SQLModel, table=True):
    __tablename__ = "works"

    id: str = Field(primary_key=True)
    title: str
    abstract: Optional[str] = None
    publication_year: Optional[int] = None
    publication_date: Optional[date] = None
    language: Optional[str] = Field(default=None, max_length=10)
    doi: Optional[str] = None
    cited_by_count: int = Field(default=0)
    is_oa: bool = Field(default=False)
    oa_status: Optional[str] = None
    oa_license: Optional[str] = None
    is_retracted: bool = Field(default=False)
    type: Optional[str] = None

    source_id: Optional[str] = Field(default=None, foreign_key="sources.id")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    raw_data: Any = Field(default=None, sa_column=Column(JSONB))

    source: Optional["Source"] = Relationship(back_populates="works")
    authors: List["Author"] = Relationship(back_populates="works", link_model=AuthorWork)
    topics: List["Topic"] = Relationship(link_model=WorkTopic)

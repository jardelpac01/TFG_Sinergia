from typing import Optional, List, Any
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone
from .author_work import AuthorWork
from .author_topic import AuthorTopic

class Author(SQLModel, table=True):
    __tablename__ = "authors"

    id: str = Field(primary_key=True)
    display_name: str
    orcid: Optional[str] = None
    h_index: int = Field(default=0)
    works_count: int = Field(default=0)
    cited_by_count: int = Field(default=0)

    counts_by_year: Any = Field(default=None, sa_column=Column(JSONB))
    raw_data: Any = Field(default=None, sa_column=Column(JSONB))

    last_known_institution_id: Optional[str] = Field(default=None, foreign_key="institutions.id")
    research_group_id: Optional[int] = Field(default=None, foreign_key="research_groups.id")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    last_known_institution: Optional["Institution"] = Relationship(back_populates="authors")
    research_group: Optional["ResearchGroup"] = Relationship(back_populates="authors")
    works: List["Work"] = Relationship(back_populates="authors", link_model=AuthorWork)
    topics: List["Topic"] = Relationship(link_model=AuthorTopic)
    user: Optional["User"] = Relationship(back_populates="author")

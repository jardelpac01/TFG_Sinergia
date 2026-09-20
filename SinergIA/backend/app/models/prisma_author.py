from typing import Optional
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone


class PrismaAuthor(SQLModel, table=True):
    __tablename__ = "prisma_authors"

    prisma_id: int = Field(primary_key=True)
    display_name: str
    department: Optional[str] = Field(default=None, max_length=255)
    research_group_code: Optional[str] = Field(default=None, max_length=50, index=True)
    research_group_name: Optional[str] = Field(default=None, max_length=255)
    orcid: Optional[str] = Field(default=None, max_length=255, unique=True)
    openalex_author_id: Optional[str] = Field(default=None, max_length=255, index=True)
    dialnet_code: Optional[str] = Field(default=None, max_length=255)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

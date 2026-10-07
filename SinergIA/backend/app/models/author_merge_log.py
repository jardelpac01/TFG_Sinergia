from typing import Optional, Any
from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, timezone


class AuthorMergeLog(SQLModel, table=True):
    __tablename__ = "author_merge_logs"

    id: Optional[int] = Field(default=None, primary_key=True)
    incoming_author_id: str = Field(max_length=255)
    incoming_display_name: str
    matched_author_id: str = Field(max_length=255, foreign_key="authors.id")
    matched_display_name: str
    score: float
    score_breakdown: Any = Field(default=None, sa_column=Column(JSONB))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

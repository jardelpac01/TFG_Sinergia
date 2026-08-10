from sqlmodel import SQLModel
from typing import Optional, List
from datetime import date, datetime
from .topic import TopicRead
from .source import SourceRead
from .author import AuthorReadLite

class WorkBase(SQLModel):
    id: str
    title: str
    publication_year: Optional[int] = None
    publication_date: Optional[date] = None
    language: Optional[str] = None
    doi: Optional[str] = None
    cited_by_count: int = 0
    is_oa: bool = False
    oa_status: Optional[str] = None
    is_retracted: bool = False
    type: Optional[str] = None

class WorkCreate(WorkBase):
    source_id: Optional[str] = None

class WorkRead(WorkBase):
    source_id: Optional[str]
    updated_at: datetime

class WorkReadWithRelationships(WorkRead):
    source: Optional[SourceRead] = None
    topics: List[TopicRead] = []
    authors: List[AuthorReadLite] = []
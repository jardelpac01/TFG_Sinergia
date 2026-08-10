from sqlmodel import SQLModel
from typing import Optional
from datetime import datetime

class SourceBase(SQLModel):
    id: str
    display_name: str
    issn: Optional[str] = None
    publisher: Optional[str] = None
    type: Optional[str] = None

class SourceCreate(SourceBase):
    pass

class SourceRead(SourceBase):
    updated_at: datetime
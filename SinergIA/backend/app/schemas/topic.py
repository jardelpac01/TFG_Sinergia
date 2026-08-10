from sqlmodel import SQLModel
from typing import Optional

class TopicBase(SQLModel):
    id: str
    display_name: str
    subfield: Optional[str] = None
    field: Optional[str] = None
    domain: Optional[str] = None

class TopicCreate(TopicBase):
    pass

class TopicRead(TopicBase):
    pass
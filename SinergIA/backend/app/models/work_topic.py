from typing import Optional
from sqlmodel import SQLModel, Field

class WorkTopic(SQLModel, table=True):
    __tablename__ = "work_topics"
    
    work_id: str = Field(foreign_key="works.id", primary_key=True)
    topic_id: str = Field(foreign_key="topics.id", primary_key=True)
    score: float = Field(default=0.0)
    is_primary: bool = Field(default=False)
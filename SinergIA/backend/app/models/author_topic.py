from typing import Optional
from sqlmodel import SQLModel, Field

class AuthorTopic(SQLModel, table=True):
    __tablename__ = "author_topics"
    
    author_id: str = Field(foreign_key="authors.id", primary_key=True)
    topic_id: str = Field(foreign_key="topics.id", primary_key=True)
    score: float = Field(default=0.0)
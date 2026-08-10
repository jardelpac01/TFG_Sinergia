from typing import Optional, Any
from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB

class Topic(SQLModel, table=True):
    __tablename__ = "topics"

    id: str = Field(primary_key=True)
    display_name: str
    subfield: Optional[str] = None
    field: Optional[str] = None
    domain: Optional[str] = None
    raw_data: Any = Field(default=None, sa_column=Column(JSONB))
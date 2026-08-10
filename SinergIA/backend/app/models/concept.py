from typing import Optional, Any
from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB


class Concept(SQLModel, table=True):
    __tablename__ = "concepts"

    id: str = Field(primary_key=True)
    display_name: str
    level: Optional[int] = None
    wikidata: Optional[str] = None
    description: Optional[str] = None
    raw_data: Any = Field(default=None, sa_column=Column(JSONB))

from typing import Optional
from sqlmodel import SQLModel, Field

class AuthorWork(SQLModel, table=True):
    __tablename__ = "author_works"

    author_id: str = Field(foreign_key="authors.id", primary_key=True)
    work_id: str = Field(foreign_key="works.id", primary_key=True)
    author_position: Optional[str] = None
    is_corresponding: bool = Field(default=False)
    raw_affiliation: Optional[str] = None
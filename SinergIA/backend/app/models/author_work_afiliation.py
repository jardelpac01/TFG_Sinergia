from typing import Optional
from sqlmodel import SQLModel, Field

class AuthorWorkAffiliation(SQLModel, table=True):
    __tablename__ = "author_work_affiliations"

    author_id: str = Field(foreign_key="authors.id", primary_key=True)
    work_id: str = Field(foreign_key="works.id", primary_key=True)
    institution_id: str = Field(foreign_key="institutions.id", primary_key=True)
    raw_affiliation: Optional[str] = None
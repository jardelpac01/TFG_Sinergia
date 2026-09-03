from typing import List, Optional
from sqlmodel import SQLModel, Field, Relationship


class ResearchGroup(SQLModel, table=True):
    __tablename__ = "research_groups"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: Optional[str] = None
    website_url: Optional[str] = None

    authors: List["Author"] = Relationship(back_populates="research_group")

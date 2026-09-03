from sqlmodel import SQLModel
from typing import Optional


class ResearchGroupBase(SQLModel):
    name: str
    description: Optional[str] = None
    website_url: Optional[str] = None


class ResearchGroupCreate(ResearchGroupBase):
    pass


class ResearchGroupRead(ResearchGroupBase):
    id: int

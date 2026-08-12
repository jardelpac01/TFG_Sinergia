from typing import Any, Optional

from sqlmodel import SQLModel


class ConceptBase(SQLModel):
    id: str
    display_name: str
    level: Optional[int] = None
    wikidata: Optional[str] = None
    description: Optional[str] = None
    raw_data: Optional[Any] = None


class ConceptCreate(ConceptBase):
    pass


class ConceptRead(ConceptBase):
    pass

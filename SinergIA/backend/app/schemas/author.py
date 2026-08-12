from sqlmodel import SQLModel
from typing import Optional, List, Any
from datetime import datetime
from .topic import TopicRead
from .institution import InstitutionRead

class AuthorBase(SQLModel):
    id: str
    display_name: str
    orcid: Optional[str] = None
    h_index: int = 0
    works_count: int = 0
    cited_by_count: int = 0
    counts_by_year: Optional[Any] = None

class AuthorCreate(AuthorBase):
    last_known_institution_id: Optional[str] = None

class AuthorRead(AuthorBase):
    last_known_institution_id: Optional[str]
    updated_at: datetime

class AuthorReadLite(SQLModel):
    id: str
    display_name: str
    orcid: Optional[str] = None

class AuthorReadWithRelationships(AuthorRead):
    last_known_institution: Optional[InstitutionRead] = None
    topics: List[TopicRead] = []

class CoAuthorConnection(SQLModel):
    id: str
    display_name: str
    shared_works_count: int

class CountryConnection(SQLModel):
    country_code: Optional[str] = None
    works_count: int

class AuthorNetwork(SQLModel):
    author: AuthorReadLite
    coauthors: List[CoAuthorConnection] = []
    country_collaborations: List[CountryConnection] = []

class AuthorReadWithWorks(AuthorReadWithRelationships):
    works: List["WorkReadLite"] = []
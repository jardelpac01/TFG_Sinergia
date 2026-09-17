from sqlmodel import SQLModel
from typing import Optional, List, Any
from datetime import datetime
from .topic import TopicRead
from .institution import InstitutionRead
from .research_group import ResearchGroupRead

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
    research_group_id: Optional[int] = None

class AuthorRead(AuthorBase):
    last_known_institution_id: Optional[str]
    research_group_id: Optional[int] = None
    updated_at: datetime

class AuthorReadLite(SQLModel):
    id: str
    display_name: str
    orcid: Optional[str] = None
    research_group_id: Optional[int] = None
    research_group_name: Optional[str] = None

class AuthorReadWithRelationships(AuthorRead):
    last_known_institution: Optional[InstitutionRead] = None
    research_group: Optional[ResearchGroupRead] = None
    topics: List[TopicRead] = []

class CoAuthorConnection(SQLModel):
    id: str
    display_name: str
    shared_works_count: int

class CountryConnection(SQLModel):
    country_code: Optional[str] = None
    works_count: int

class CityConnection(SQLModel):
    city: Optional[str] = None
    country_code: Optional[str] = None
    geo_lat: float
    geo_lon: float
    authors_count: int

class WorksByYear(SQLModel):
    year: int
    works_count: int

class AuthorNetwork(SQLModel):
    author: AuthorReadLite
    coauthors: List[CoAuthorConnection] = []
    country_collaborations: List[CountryConnection] = []
    city_collaborations: List[CityConnection] = []
    works_by_year: List[WorksByYear] = []

class CoAuthorLocation(SQLModel):
    id: str
    display_name: str
    orcid: Optional[str] = None
    shared_works_count: int
    institution_name: Optional[str] = None
    country_code: Optional[str] = None
    city: Optional[str] = None

class AuthorCollaboratorsResponse(SQLModel):
    author: AuthorReadLite
    collaborators: List[CoAuthorLocation] = []

class AuthorReadWithWorks(AuthorReadWithRelationships):
    works: List["WorkReadLite"] = []

class AuthorListResponse(SQLModel):
    items: List[AuthorReadLite]
    total: int
    page: int
    page_size: int
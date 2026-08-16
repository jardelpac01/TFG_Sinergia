from typing import List, Optional

from sqlmodel import SQLModel, Field


class OpenAlexAuthorsBatchIngestRequest(SQLModel):
    orcids: List[str] = Field(default_factory=list)


class OpenAlexAuthorsBatchIngestItem(SQLModel):
    orcid: str
    status: str
    author_id: Optional[str] = None
    error: Optional[str] = None


class OpenAlexAuthorsBatchIngestResponse(SQLModel):
    requested: int
    ingested: int
    failed: int
    results: List[OpenAlexAuthorsBatchIngestItem] = Field(default_factory=list)

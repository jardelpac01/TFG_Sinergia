from typing import List, Optional

from sqlmodel import Field, SQLModel


class OpenAlexAuthorsBatchIngestRequest(SQLModel):
    orcids: List[str] = Field(default_factory=list)


class OpenAlexAuthorsBatchIdentifiersRequest(SQLModel):
    identifiers: List[str] = Field(
        default_factory=list,
        description=(
            "OpenAlex author identifiers. Each value may be an OpenAlex author ID, "
            "an ORCID, or a full OpenAlex author URL."
        ),
        schema_extra={
            "example": [
                "A1234567890",
                "0000-0000-0000-0000",
                "https://openalex.org/A1234567890",
            ]
        },
    )


class OpenAlexAuthorIngestionRequest(SQLModel):
    identifier: str = Field(
        min_length=1,
        description="An OpenAlex author ID, an ORCID, or a full OpenAlex author URL.",
        schema_extra={"example": "A1234567890"},
    )


class OpenAlexWorkIngestionRequest(SQLModel):
    identifier: str = Field(
        min_length=1,
        description="An OpenAlex work ID or a full OpenAlex work URL.",
        schema_extra={"example": "W1234567890"},
    )


class OpenAlexAuthorsBatchIngestItem(SQLModel):
    identifier: str
    status: str
    author_id: Optional[str] = None
    error: Optional[str] = None


class OpenAlexAuthorsBatchIngestResponse(SQLModel):
    requested: int
    ingested: int
    failed: int
    results: List[OpenAlexAuthorsBatchIngestItem] = Field(default_factory=list)


class OpenAlexAuthorSearchItem(SQLModel):
    openalex_id: str
    display_name: str
    display_name_alternatives: List[str] = Field(default_factory=list)
    orcid: Optional[str] = None
    works_count: int = 0
    cited_by_count: int = 0
    last_known_institution: Optional[str] = None


class OpenAlexAuthorSearchResponse(SQLModel):
    query: str
    page: int
    per_page: int
    total_results: int
    results: List[OpenAlexAuthorSearchItem] = Field(default_factory=list)


class OpenAlexAuthorSearchAndIngestRequest(SQLModel):
    name: str = Field(min_length=2)
    force: bool = False
    per_page: int = Field(default=10, ge=1, le=25)


class OpenAlexAuthorSearchAndIngestResponse(SQLModel):
    query: str
    status: str
    total_results: int
    selected_by: Optional[str] = None
    author_id: Optional[str] = None
    candidates: List[OpenAlexAuthorSearchItem] = Field(default_factory=list)

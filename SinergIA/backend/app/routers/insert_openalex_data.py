from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.database import get_db
from app.schemas.openalex_ingestion import (
    OpenAlexAuthorIngestionRequest,
    OpenAlexAuthorSearchAndIngestRequest,
    OpenAlexAuthorSearchAndIngestResponse,
    OpenAlexAuthorSearchItem,
    OpenAlexAuthorSearchResponse,
    OpenAlexAuthorsBatchIdentifiersRequest,
    OpenAlexAuthorsBatchIngestRequest,
    OpenAlexAuthorsBatchIngestResponse,
    OpenAlexWorkIngestionRequest,
    PrismaDepartmentIngestItem,
    PrismaDepartmentIngestionRequest,
    PrismaDepartmentIngestionResponse,
)
from app.services.openalex_data import (
    AuthorNotFoundError,
    OpenAlexService,
    OpenAlexUpstreamError,
    WorkNotFoundError,
)


router = APIRouter(prefix="/openalex", tags=["openalex"])


@router.get("/authors/search", response_model=OpenAlexAuthorSearchResponse)
def search_authors(
    name: str = Query(..., min_length=2),
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=25),
    db: Session = Depends(get_db),
):
    service = OpenAlexService(db)
    try:
        total_results, items = service.search_authors_by_name(name=name, page=page, per_page=per_page)
    except OpenAlexUpstreamError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return OpenAlexAuthorSearchResponse(
        query=name,
        page=page,
        per_page=per_page,
        total_results=total_results,
        results=[OpenAlexAuthorSearchItem(**item) for item in items],
    )


@router.post(
    "/author-ingestions/from-name",
    response_model=OpenAlexAuthorSearchAndIngestResponse,
)
def ingest_author_from_name_search(
    payload: OpenAlexAuthorSearchAndIngestRequest, db: Session = Depends(get_db)
):
    service = OpenAlexService(db)
    try:
        result = service.search_and_ingest_author_by_name(
            name=payload.name,
            force=payload.force,
            per_page=payload.per_page,
        )
    except OpenAlexUpstreamError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return OpenAlexAuthorSearchAndIngestResponse(
        query=payload.name,
        status=result.status,
        total_results=result.total_results,
        selected_by=result.selected_by,
        author_id=result.author_id,
        candidates=[
            OpenAlexAuthorSearchItem(**candidate)
            for candidate in result.candidates
        ],
    )


@router.post("/author-ingestions/batch-orcids", response_model=OpenAlexAuthorsBatchIngestResponse)
def ingest_authors_by_orcid_batch(
    payload: OpenAlexAuthorsBatchIngestRequest, db: Session = Depends(get_db)
):
    if not payload.orcids:
        raise HTTPException(status_code=400, detail="The ORCID list cannot be empty.")

    service = OpenAlexService(db)
    return service.ingest_authors_batch(
        identifiers=payload.orcids,
        ingest_author=service.fetch_and_store_author,
        empty_identifier_message="ORCID value is empty.",
        not_found_message="No author was found in OpenAlex for this ORCID.",
    )


@router.post("/author-ingestions/batch", response_model=OpenAlexAuthorsBatchIngestResponse)
def ingest_authors_by_identifier_batch(
    payload: OpenAlexAuthorsBatchIdentifiersRequest, db: Session = Depends(get_db)
):
    if not payload.identifiers:
        raise HTTPException(status_code=400, detail="The identifiers list cannot be empty.")

    service = OpenAlexService(db)
    return service.ingest_authors_batch(
        identifiers=payload.identifiers,
        ingest_author=service.fetch_and_store_author_by_identifier,
        empty_identifier_message="Identifier value is empty.",
        not_found_message="No author was found in OpenAlex for this identifier.",
    )


@router.post(
    "/author-ingestions/batch-prisma-department",
    response_model=PrismaDepartmentIngestionResponse,
)
def ingest_authors_by_prisma_department(
    payload: PrismaDepartmentIngestionRequest, db: Session = Depends(get_db)
):
    service = OpenAlexService(db)
    try:
        raw_results = service.ingest_authors_by_prisma_department(payload.department_code)
    except OpenAlexUpstreamError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    results = [PrismaDepartmentIngestItem(**item) for item in raw_results]
    created = sum(1 for item in results if item.status == "created")
    updated = sum(1 for item in results if item.status == "updated")
    skipped = sum(1 for item in results if item.status == "skipped")
    failed = sum(1 for item in results if item.status == "failed")

    return PrismaDepartmentIngestionResponse(
        department_code=payload.department_code,
        requested=len(results),
        created=created,
        updated=updated,
        skipped=skipped,
        failed=failed,
        results=results,
    )


@router.post("/author-ingestions")
def ingest_author_by_identifier(
    payload: OpenAlexAuthorIngestionRequest | None = None,
    author_identifier: str | None = None,
    db: Session = Depends(get_db),
):
    identifier = author_identifier if author_identifier is not None else (payload.identifier if payload else "")
    if not identifier:
        raise HTTPException(status_code=400, detail="Author identifier is required.")

    service = OpenAlexService(db)
    try:
        author_id = service.fetch_and_store_author_or_raise(identifier)
    except AuthorNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except OpenAlexUpstreamError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {
        "message": "OpenAlex author data ingested successfully.",
        "author_id": author_id,
        "author_identifier": identifier,
    }


@router.post("/work-ingestions")
def ingest_work_by_identifier(
    payload: OpenAlexWorkIngestionRequest | None = None,
    work_identifier: str | None = None,
    db: Session = Depends(get_db),
):
    identifier = work_identifier if work_identifier is not None else (payload.identifier if payload else "")
    if not identifier:
        raise HTTPException(status_code=400, detail="Work identifier is required.")

    service = OpenAlexService(db)
    try:
        work_id = service.fetch_and_store_work_or_raise(identifier)
    except WorkNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except OpenAlexUpstreamError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {
        "message": "OpenAlex work data ingested successfully.",
        "work_id": work_id,
        "work_identifier": identifier,
    }

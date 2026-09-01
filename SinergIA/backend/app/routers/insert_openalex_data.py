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
    OpenAlexAuthorsBatchIngestItem,
    OpenAlexAuthorsBatchIngestRequest,
    OpenAlexAuthorsBatchIngestResponse,
    OpenAlexWorkIngestionRequest,
)
from app.services.openalex_data import OpenAlexService, OpenAlexUpstreamError


router = APIRouter(prefix="/openalex", tags=["openalex"])


def _ingest_author_identifier(service: OpenAlexService, author_identifier: str) -> str:
    try:
        author_id = service.fetch_and_store_author_by_identifier(author_identifier)
    except OpenAlexUpstreamError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if not author_id:
        raise HTTPException(
            status_code=404,
            detail=f"No author was found for identifier {author_identifier}.",
        )
    return author_id


def _ingest_work_identifier(service: OpenAlexService, work_identifier: str) -> str:
    try:
        work_id = service.fetch_and_store_work_by_identifier(work_identifier)
    except OpenAlexUpstreamError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if not work_id:
        raise HTTPException(
            status_code=404,
            detail=f"No work was found for identifier {work_identifier}.",
        )
    return work_id


def _ingest_author_identifier_batch(
    service: OpenAlexService, identifiers: list[str]
) -> OpenAlexAuthorsBatchIngestResponse:
    if not identifiers:
        raise HTTPException(status_code=400, detail="The identifiers list cannot be empty.")

    results: list[OpenAlexAuthorsBatchIngestItem] = []
    ingested = 0
    failed = 0

    for raw_identifier in identifiers:
        identifier = raw_identifier.strip()
        if not identifier:
            failed += 1
            results.append(
                OpenAlexAuthorsBatchIngestItem(
                    identifier=raw_identifier,
                    status="failed",
                    error="Identifier value is empty.",
                )
            )
            continue

        try:
            author_id = service.fetch_and_store_author_by_identifier(identifier)
        except ValueError as exc:
            failed += 1
            results.append(
                OpenAlexAuthorsBatchIngestItem(
                    identifier=identifier,
                    status="failed",
                    error=str(exc),
                )
            )
            continue
        except OpenAlexUpstreamError as exc:
            failed += 1
            results.append(
                OpenAlexAuthorsBatchIngestItem(
                    identifier=identifier,
                    status="failed",
                    error=str(exc),
                )
            )
            continue

        if not author_id:
            failed += 1
            results.append(
                OpenAlexAuthorsBatchIngestItem(
                    identifier=identifier,
                    status="failed",
                    error="No author was found in OpenAlex for this identifier.",
                )
            )
            continue

        ingested += 1
        results.append(
            OpenAlexAuthorsBatchIngestItem(
                identifier=identifier,
                status="ingested",
                author_id=author_id,
            )
        )

    return OpenAlexAuthorsBatchIngestResponse(
        requested=len(identifiers),
        ingested=ingested,
        failed=failed,
        results=results,
    )


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
        status=result["status"],
        total_results=int(result.get("total_results", 0) or 0),
        selected_by=result.get("selected_by"),
        author_id=result.get("author_id"),
        candidates=[
            OpenAlexAuthorSearchItem(**candidate)
            for candidate in result.get("candidates", [])
        ],
    )


@router.post("/author-ingestions/batch-orcids", response_model=OpenAlexAuthorsBatchIngestResponse)
def ingest_authors_by_orcid_batch(
    payload: OpenAlexAuthorsBatchIngestRequest, db: Session = Depends(get_db)
):
    if not payload.orcids:
        raise HTTPException(status_code=400, detail="The ORCID list cannot be empty.")

    service = OpenAlexService(db)
    results: list[OpenAlexAuthorsBatchIngestItem] = []
    ingested = 0
    failed = 0

    for raw_orcid in payload.orcids:
        orcid = raw_orcid.strip()
        if not orcid:
            failed += 1
            results.append(
                OpenAlexAuthorsBatchIngestItem(
                    identifier=raw_orcid,
                    status="failed",
                    error="ORCID value is empty.",
                )
            )
            continue

        try:
            author_id = service.fetch_and_store_author(orcid)
        except ValueError as exc:
            failed += 1
            results.append(
                OpenAlexAuthorsBatchIngestItem(
                    identifier=orcid,
                    status="failed",
                    error=str(exc),
                )
            )
            continue
        except OpenAlexUpstreamError as exc:
            failed += 1
            results.append(
                OpenAlexAuthorsBatchIngestItem(
                    identifier=orcid,
                    status="failed",
                    error=str(exc),
                )
            )
            continue

        if not author_id:
            failed += 1
            results.append(
                OpenAlexAuthorsBatchIngestItem(
                    identifier=orcid,
                    status="failed",
                    error="No author was found in OpenAlex for this ORCID.",
                )
            )
            continue

        ingested += 1
        results.append(
            OpenAlexAuthorsBatchIngestItem(
                identifier=orcid,
                status="ingested",
                author_id=author_id,
            )
        )

    return OpenAlexAuthorsBatchIngestResponse(
        requested=len(payload.orcids),
        ingested=ingested,
        failed=failed,
        results=results,
    )


@router.post("/author-ingestions/batch", response_model=OpenAlexAuthorsBatchIngestResponse)
def ingest_authors_by_identifier_batch(
    payload: OpenAlexAuthorsBatchIdentifiersRequest, db: Session = Depends(get_db)
):
    service = OpenAlexService(db)
    return _ingest_author_identifier_batch(service, payload.identifiers)


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
    author_id = _ingest_author_identifier(service, identifier)

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
    work_id = _ingest_work_identifier(service, identifier)

    return {
        "message": "OpenAlex work data ingested successfully.",
        "work_id": work_id,
        "work_identifier": identifier,
    }

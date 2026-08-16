from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_db
from app.schemas.openalex_ingestion import (
    OpenAlexAuthorsBatchIngestRequest,
    OpenAlexAuthorsBatchIngestResponse,
    OpenAlexAuthorsBatchIngestItem,
)
from app.services.openalex_data import OpenAlexService


router = APIRouter(prefix="/openalex", tags=["openalex"])


@router.post("/authors/batch", response_model=OpenAlexAuthorsBatchIngestResponse)
def insert_authors_batch(
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
                    orcid=raw_orcid,
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
                    orcid=orcid,
                    status="failed",
                    error=str(exc),
                )
            )
            continue

        if not author_id:
            failed += 1
            results.append(
                OpenAlexAuthorsBatchIngestItem(
                    orcid=orcid,
                    status="failed",
                    error="No author was found in OpenAlex for this ORCID.",
                )
            )
            continue

        ingested += 1
        results.append(
            OpenAlexAuthorsBatchIngestItem(
                orcid=orcid,
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


@router.post("/authors/{author_identifier}")
def insert_author(author_identifier: str, db: Session = Depends(get_db)):
    service = OpenAlexService(db)
    author_id = service.fetch_and_store_author_by_identifier(author_identifier)

    if not author_id:
        raise HTTPException(
            status_code=404,
            detail=f"No author was found for identifier {author_identifier}.",
        )

    return {
        "message": "OpenAlex author data ingested successfully.",
        "author_id": author_id,
        "author_identifier": author_identifier,
    }


@router.post("/works/{work_identifier}")
def insert_work(work_identifier: str, db: Session = Depends(get_db)):
    service = OpenAlexService(db)
    work_id = service.fetch_and_store_work_by_identifier(work_identifier)

    if not work_id:
        raise HTTPException(
            status_code=404,
            detail=f"No work was found for identifier {work_identifier}.",
        )

    return {
        "message": "OpenAlex work data ingested successfully.",
        "work_id": work_id,
        "work_identifier": work_identifier,
    }

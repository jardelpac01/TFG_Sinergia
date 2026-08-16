from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_db
from app.models import Author
from app.schemas.author import AuthorReadLite
from app.schemas.work import WorkReadWithRelationships
from app.services.author_service import AuthorService


router = APIRouter(prefix="/authors", tags=["authors"])


@router.get("/{author_id}", response_model=AuthorReadLite)
def get_author(author_id: str, db: Session = Depends(get_db)):
    service = AuthorService(db)
    author = service.get_author(author_id)

    if not author:
        raise HTTPException(status_code=404, detail=f"Author with id '{author_id}' was not found.")

    return AuthorReadLite(
        id=author.id,
        display_name=author.display_name,
        orcid=author.orcid,
    )


@router.get("/{author_id}/works", response_model=List[WorkReadWithRelationships])
def get_author_works(author_id: str, db: Session = Depends(get_db)):
    service = AuthorService(db)
    author = service.get_author(author_id)

    if not author:
        raise HTTPException(status_code=404, detail=f"Author with id '{author_id}' was not found.")

    works = service.get_author_works(author_id)
    return [
        WorkReadWithRelationships(
            id=work.id,
            title=work.title,
            publication_year=work.publication_year,
            publication_date=work.publication_date,
            language=work.language,
            doi=work.doi,
            cited_by_count=work.cited_by_count,
            is_oa=work.is_oa,
            oa_status=work.oa_status,
            is_retracted=work.is_retracted,
            type=work.type,
            source_id=work.source_id,
            updated_at=work.updated_at,
            source=work.source,
            topics=work.topics,
            authors=[
                AuthorReadLite(
                    id=author_item.id,
                    display_name=author_item.display_name,
                    orcid=author_item.orcid,
                )
                for author_item in work.authors
            ],
        )
        for work in works
    ]

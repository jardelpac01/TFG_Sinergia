from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.database import get_db
from app.schemas.author import AuthorNetwork, AuthorReadLite
from app.schemas.work import WorkReadWithRelationships
from app.services.author_service import AuthorService


router = APIRouter(prefix="/authors", tags=["authors"])


@router.get("", response_model=List[AuthorReadLite])
def list_authors(
    q: Optional[str] = Query(default=None, description="Search authors by name or ORCID"),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    service = AuthorService(db)
    return service.list_authors(q=q, limit=limit)

@router.get("/{author_id}", response_model=AuthorReadLite)
def get_author(author_id: str, db: Session = Depends(get_db)):
    service = AuthorService(db)
    author = service.get_author(author_id)

    if not author:
        raise HTTPException(status_code=404, detail=f"Author with id '{author_id}' was not found.")

    return author


@router.get("/{author_id}/works", response_model=List[WorkReadWithRelationships])
def get_author_works(author_id: str, db: Session = Depends(get_db)):
    service = AuthorService(db)
    author = service.get_author(author_id)

    if not author:
        raise HTTPException(status_code=404, detail=f"Author with id '{author_id}' was not found.")

    return service.get_author_works(author_id)



@router.get("/{author_id}/network", response_model=AuthorNetwork)
def get_author_network(author_id: str, db: Session = Depends(get_db)):
    service = AuthorService(db)
    network = service.get_author_network(author_id)
    if not network:
        raise HTTPException(status_code=404, detail=f"Author with id '{author_id}' was not found.")
    return network

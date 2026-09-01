from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.database import get_db
from app.schemas.author import AuthorReadLite
from app.schemas.work import WorkReadLite, WorkReadWithRelationships
from app.services.work_service import WorkService


router = APIRouter(prefix="/works", tags=["works"])


@router.get("", response_model=List[WorkReadLite])
def list_works(
    q: Optional[str] = Query(default=None, description="Search by title or DOI"),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    service = WorkService(db)
    return service.list_works(q=q, limit=limit)


@router.get("/{work_id}", response_model=WorkReadWithRelationships)
def read_work(work_id: str, db: Session = Depends(get_db)):
    service = WorkService(db)
    work = service.get_work(work_id)
    if not work:
        raise HTTPException(status_code=404, detail="Work not found")
    return work


@router.get("/{work_id}/authors", response_model=List[AuthorReadLite])
def read_work_authors(work_id: str, db: Session = Depends(get_db)):
    service = WorkService(db)
    authors = service.get_work_authors(work_id)
    if authors is None:
        raise HTTPException(status_code=404, detail="Work not found")
    return authors


from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.database import get_db
from app.schemas.author import AuthorReadLite
from app.schemas.institution import InstitutionListResponse, InstitutionRead
from app.services.institution_service import InstitutionService


router = APIRouter(prefix="/institutions", tags=["institutions"])


@router.get("", response_model=InstitutionListResponse)
def list_institutions(
    q: Optional[str] = Query(default=None, description="Search institution by name or country code"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=18, ge=1, le=200),
    db: Session = Depends(get_db),
):
    service = InstitutionService(db)
    offset = (page - 1) * page_size
    items, total = service.list_institutions(q=q, limit=page_size, offset=offset)
    return InstitutionListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{institution_id}", response_model=InstitutionRead)
def read_institution(institution_id: str, db: Session = Depends(get_db)):
    service = InstitutionService(db)
    institution = service.get_institution(institution_id)
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")
    return institution


@router.get("/{institution_id}/authors", response_model=List[AuthorReadLite])
def list_institution_authors(institution_id: str, db: Session = Depends(get_db)):
    service = InstitutionService(db)
    authors = service.get_institution_authors(institution_id)
    if authors is None:
        raise HTTPException(status_code=404, detail="Institution not found")
    return authors


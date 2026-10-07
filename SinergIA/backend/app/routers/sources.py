from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.database import get_db
from app.schemas.source import SourceRead
from app.services.source_service import SourceService


router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("", response_model=List[SourceRead])
def list_sources(
    q: Optional[str] = Query(default=None, description="Search source by name or publisher"),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    service = SourceService(db)
    return service.list_sources(q=q, limit=limit)


@router.get("/{source_id}", response_model=SourceRead)
def read_source(source_id: str, db: Session = Depends(get_db)):
    service = SourceService(db)
    source = service.get_source(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return source


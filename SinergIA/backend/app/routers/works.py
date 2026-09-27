import csv
import re
import unicodedata
from collections import defaultdict
from datetime import date
from io import StringIO
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlmodel import Session

from app.database import get_db
from app.schemas.author import AuthorReadLite
from app.schemas.work import WorkListResponse, WorkReadWithRelationships
from app.services.work_service import WorkService
from app.utils.dates import month_end, month_start


router = APIRouter(prefix="/works", tags=["works"])


def _csv_safe(value: object) -> object:
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return f"'{value}"
    return value


def _normalized_title(title: str) -> str:
    normalized = unicodedata.normalize("NFD", title)
    without_accents = "".join(
        character
        for character in normalized
        if unicodedata.category(character) != "Mn"
    )
    return re.sub(r"[^a-z0-9]+", " ", without_accents.lower()).strip()


def _group_export_works(works):
    groups = defaultdict(list)
    for work in works:
        title_key = _normalized_title(work.title) or work.id
        groups[(title_key, work.publication_year)].append(work)
    return list(groups.values())


@router.get("", response_model=WorkListResponse)
def list_works(
    q: Optional[str] = Query(default=None, description="Search by title or DOI"),
    from_month: Optional[str] = Query(
        default=None, pattern=r"^\d{4}-(0[1-9]|1[0-2])$"
    ),
    to_month: Optional[str] = Query(
        default=None, pattern=r"^\d{4}-(0[1-9]|1[0-2])$"
    ),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=200),
    db: Session = Depends(get_db),
):
    from_date = month_start(from_month)
    to_date = month_end(to_month)
    if from_date and to_date and from_date > to_date:
        raise HTTPException(
            status_code=422,
            detail="The start month cannot be later than the end month.",
        )
    offset = (page - 1) * page_size
    items, total = WorkService(db).list_works(
        q=q,
        from_date=from_date,
        to_date=to_date,
        limit=page_size,
        offset=offset,
    )
    return WorkListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/export")
def export_works(
    q: Optional[str] = Query(default=None, description="Filter by title or DOI"),
    author_q: Optional[str] = Query(
        default=None, description="Filter by author name or ORCID"
    ),
    author_id: Optional[str] = Query(default=None),
    research_group_id: Optional[int] = Query(default=None),
    institution_id: Optional[str] = Query(default=None),
    topic_id: Optional[str] = Query(default=None),
    from_month: Optional[str] = Query(
        default=None, pattern=r"^\d{4}-(0[1-9]|1[0-2])$"
    ),
    to_month: Optional[str] = Query(
        default=None, pattern=r"^\d{4}-(0[1-9]|1[0-2])$"
    ),
    db: Session = Depends(get_db),
):
    from_date = month_start(from_month)
    to_date = month_end(to_month)
    if from_date and to_date and from_date > to_date:
        raise HTTPException(
            status_code=422,
            detail="The start month cannot be later than the end month.",
        )

    works = WorkService(db).list_works_for_export(
        q=q,
        author_q=author_q,
        author_id=author_id,
        research_group_id=research_group_id,
        institution_id=institution_id,
        topic_id=topic_id,
        from_date=from_date,
        to_date=to_date,
    )

    output = StringIO(newline="")
    writer = csv.writer(output, delimiter=";", quoting=csv.QUOTE_MINIMAL)
    writer.writerow(
        [
            "Título",
            "Fecha de publicación",
            "Año",
            "DOI",
            "Tipo",
            "Citas",
            "Acceso abierto",
            "Estado de acceso abierto",
            "Fuente",
            "Investigadores",
            "Temas",
        ]
    )
    for versions in _group_export_works(works):
        work = max(
            versions,
            key=lambda item: (
                item.cited_by_count,
                item.publication_date or date.min,
            ),
        )
        dois = sorted({item.doi for item in versions if item.doi})
        sources = sorted(
            {
                item.source.display_name
                for item in versions
                if item.source and item.source.display_name
            }
        )
        authors = sorted(
            {
                author.display_name
                for item in versions
                for author in item.authors
            }
        )
        topics = sorted(
            {
                topic.display_name
                for item in versions
                for topic in item.topics
            }
        )
        writer.writerow(
            [
                _csv_safe(work.title),
                work.publication_date.isoformat() if work.publication_date else "",
                work.publication_year or "",
                _csv_safe(" | ".join(dois)),
                _csv_safe(work.type or ""),
                max(item.cited_by_count for item in versions),
                "Sí" if any(item.is_oa for item in versions) else "No",
                _csv_safe(work.oa_status or ""),
                _csv_safe(" | ".join(sources)),
                _csv_safe(" | ".join(authors)),
                _csv_safe(" | ".join(topics)),
            ]
        )

    return Response(
        content=f"\ufeff{output.getvalue()}",
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="publicaciones.csv"'},
    )


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

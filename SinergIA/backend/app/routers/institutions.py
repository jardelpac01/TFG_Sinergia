import csv
from io import StringIO
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlmodel import Session

from app.database import get_db
from app.schemas.author import AuthorListResponse
from app.schemas.institution import InstitutionListResponse, InstitutionRead
from app.services.institution_service import InstitutionService


router = APIRouter(prefix="/institutions", tags=["institutions"])


def _csv_safe(value: object) -> object:
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@")):
        return f"'{value}"
    return value


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


@router.get("/export")
def export_institutions(
    q: Optional[str] = Query(default=None, description="Search institution by name or country code"),
    db: Session = Depends(get_db),
):
    institutions = InstitutionService(db).list_institutions_for_export(q=q)

    output = StringIO(newline="")
    writer = csv.writer(output, delimiter=";", quoting=csv.QUOTE_MINIMAL)
    writer.writerow(
        [
            "Nombre",
            "Tipo",
            "ROR",
            "País",
            "Ciudad",
            "Latitud",
            "Longitud",
            "Web",
            "Alias",
            "Número de investigadores",
            "Investigadores",
        ]
    )
    for institution in institutions:
        aliases = institution.aliases or []
        if isinstance(aliases, list):
            aliases_text = " | ".join(str(alias) for alias in aliases)
        else:
            aliases_text = str(aliases)
        researchers = sorted(
            author.display_name
            for author in institution.authors
            if author.display_name
        )
        writer.writerow(
            [
                _csv_safe(institution.name),
                _csv_safe(institution.type or ""),
                _csv_safe(institution.ror or ""),
                _csv_safe(institution.country_code or ""),
                _csv_safe(institution.city or ""),
                institution.geo_lat if institution.geo_lat is not None else "",
                institution.geo_lon if institution.geo_lon is not None else "",
                _csv_safe(institution.homepage_url or ""),
                _csv_safe(aliases_text),
                len(researchers),
                _csv_safe(" | ".join(researchers)),
            ]
        )

    return Response(
        content=f"\ufeff{output.getvalue()}",
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="instituciones.csv"'},
    )


@router.get("/{institution_id}", response_model=InstitutionRead)
def read_institution(institution_id: str, db: Session = Depends(get_db)):
    service = InstitutionService(db)
    institution = service.get_institution(institution_id)
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")
    return institution


@router.get("/{institution_id}/authors", response_model=AuthorListResponse)
def list_institution_authors(
    institution_id: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=15, ge=1, le=200),
    db: Session = Depends(get_db),
):
    service = InstitutionService(db)
    offset = (page - 1) * page_size
    result = service.get_institution_authors(
        institution_id, limit=page_size, offset=offset
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Institution not found")
    items, total = result
    return AuthorListResponse(
        items=items, total=total, page=page, page_size=page_size
    )

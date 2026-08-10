from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.database import get_db
from app.services.openalex_data import OpenAlexService


router = APIRouter(prefix="/insert-openalex-data", tags=["openalex"])


@router.post("/{orcid}")
def insert_openalex_data(orcid: str, db: Session = Depends(get_db)):
    service = OpenAlexService(db)
    author_id = service.fetch_and_store_author(orcid)

    if not author_id:
        raise HTTPException(
            status_code=404,
            detail=f"No se ha encontrado ningun autor para el ORCID {orcid}.",
        )

    return {
        "message": "Datos de OpenAlex insertados correctamente.",
        "author_id": author_id,
        "orcid": orcid,
    }

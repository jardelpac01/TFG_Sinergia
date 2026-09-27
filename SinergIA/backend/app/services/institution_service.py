from typing import Optional

from sqlmodel import Session

from app.models import Institution
from app.repositories.institution_repository import InstitutionRepository


class InstitutionService:
    def __init__(self, db: Session):
        self.repository = InstitutionRepository(db)

    def list_institutions(self, q: Optional[str] = None, limit: int = 50, offset: int = 0):
        return self.repository.list_institutions(q=q, limit=limit, offset=offset)

    def list_institutions_for_export(self, q: Optional[str] = None):
        return self.repository.list_institutions_for_export(q=q)

    def get_institution(self, institution_id: str) -> Optional[Institution]:
        return self.repository.get_institution(institution_id)

    def get_institution_authors(
        self, institution_id: str, limit: int = 15, offset: int = 0
    ):
        if not self.repository.get_institution(institution_id):
            return None
        return self.repository.get_institution_authors(
            institution_id, limit=limit, offset=offset
        )

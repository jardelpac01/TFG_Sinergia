from typing import List, Optional

from sqlmodel import Session

from app.models import Author, Institution
from app.repositories.institution_repository import InstitutionRepository


class InstitutionService:
    def __init__(self, db: Session):
        self.repository = InstitutionRepository(db)

    def list_institutions(self, q: Optional[str] = None, limit: int = 50) -> List[Institution]:
        return self.repository.list_institutions(q=q, limit=limit)

    def get_institution(self, institution_id: str) -> Optional[Institution]:
        return self.repository.get_institution(institution_id)

    def get_institution_authors(self, institution_id: str) -> Optional[List[Author]]:
        if not self.repository.get_institution(institution_id):
            return None
        return self.repository.get_institution_authors(institution_id)

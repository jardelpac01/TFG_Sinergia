from typing import List, Optional

from sqlmodel import Session

from app.models import Source
from app.repositories.source_repository import SourceRepository


class SourceService:
    def __init__(self, db: Session):
        self.repository = SourceRepository(db)

    def list_sources(self, q: Optional[str] = None, limit: int = 50) -> List[Source]:
        return self.repository.list_sources(q=q, limit=limit)

    def get_source(self, source_id: str) -> Optional[Source]:
        return self.repository.get_source(source_id)

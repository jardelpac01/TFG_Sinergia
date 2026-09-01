from typing import List, Optional

from sqlmodel import Session

from app.models import Author, Work
from app.repositories.work_repository import WorkRepository


class WorkService:
    def __init__(self, db: Session):
        self.repository = WorkRepository(db)

    def list_works(self, q: Optional[str] = None, limit: int = 50) -> List[Work]:
        return self.repository.list_works(q=q, limit=limit)

    def get_work(self, work_id: str) -> Optional[Work]:
        return self.repository.get_work(work_id)

    def get_work_authors(self, work_id: str) -> Optional[List[Author]]:
        if not self.repository.work_exists(work_id):
            return None
        return self.repository.get_work_authors(work_id)

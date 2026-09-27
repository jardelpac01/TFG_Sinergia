from datetime import date
from typing import List, Optional

from sqlmodel import Session

from app.models import Author, Work
from app.repositories.work_repository import WorkRepository


class WorkService:
    def __init__(self, db: Session):
        self.repository = WorkRepository(db)

    def list_works(
        self,
        q: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        limit: int = 10,
        offset: int = 0,
    ):
        return self.repository.list_works(
            q=q,
            from_date=from_date,
            to_date=to_date,
            limit=limit,
            offset=offset,
        )

    def get_work(self, work_id: str) -> Optional[Work]:
        return self.repository.get_work(work_id)

    def get_work_authors(self, work_id: str) -> Optional[List[Author]]:
        if not self.repository.work_exists(work_id):
            return None
        return self.repository.get_work_authors(work_id)

    def list_works_for_export(
        self,
        q: Optional[str] = None,
        author_q: Optional[str] = None,
        author_id: Optional[str] = None,
        research_group_id: Optional[int] = None,
        institution_id: Optional[str] = None,
        topic_id: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> List[Work]:
        return self.repository.list_works_for_export(
            q=q,
            author_q=author_q,
            author_id=author_id,
            research_group_id=research_group_id,
            institution_id=institution_id,
            topic_id=topic_id,
            from_date=from_date,
            to_date=to_date,
        )

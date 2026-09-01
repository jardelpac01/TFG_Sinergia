from typing import Optional

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.models import Author, AuthorWork, Work


class WorkRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_works(self, q: Optional[str] = None, limit: int = 50):
        statement = select(Work)
        if q:
            search = f"%{q.lower()}%"
            statement = statement.where((Work.title.ilike(search)) | (Work.doi.ilike(search)))
        statement = statement.order_by(
            Work.publication_year.desc().nulls_last(), Work.title.asc()
        ).limit(limit)
        return self.db.exec(statement).all()

    def get_work(self, work_id: str) -> Optional[Work]:
        statement = (
            select(Work)
            .where(Work.id == work_id)
            .options(
                selectinload(Work.source),
                selectinload(Work.topics),
                selectinload(Work.authors),
            )
        )
        return self.db.exec(statement).one_or_none()

    def work_exists(self, work_id: str) -> bool:
        return self.db.get(Work, work_id) is not None

    def get_work_authors(self, work_id: str):
        statement = (
            select(Author)
            .join(AuthorWork, Author.id == AuthorWork.author_id)
            .where(AuthorWork.work_id == work_id)
            .order_by(Author.display_name.asc())
        )
        return self.db.exec(statement).all()

from datetime import date
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.models import (
    Author,
    AuthorWork,
    AuthorWorkAffiliation,
    Work,
    WorkTopic,
)


class WorkRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_works(self, q: Optional[str] = None, limit: int = 50):
        statement = select(Work)
        if q:
            search = f"%{q.lower()}%"
            statement = statement.where(
                (func.unaccent(func.lower(Work.title)).ilike(func.unaccent(search)))
                | (Work.doi.ilike(search))
            )
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
    ):
        statement = select(Work).options(
            selectinload(Work.source),
            selectinload(Work.topics),
            selectinload(Work.authors),
        )

        if q:
            search = f"%{q.lower()}%"
            statement = statement.where(
                func.unaccent(func.lower(Work.title)).ilike(func.unaccent(search))
                | Work.doi.ilike(search)
            )

        author_filters = []
        if author_id:
            author_filters.append(Author.id == author_id)
        if research_group_id is not None:
            author_filters.append(Author.research_group_id == research_group_id)
        if author_q:
            author_search = f"%{author_q.lower()}%"
            author_filters.append(
                func.unaccent(func.lower(Author.display_name)).ilike(
                    func.unaccent(author_search)
                )
                | Author.orcid.ilike(author_search)
            )
        if author_filters:
            matching_work_ids = (
                select(AuthorWork.work_id)
                .join(Author, Author.id == AuthorWork.author_id)
                .where(*author_filters)
            )
            statement = statement.where(Work.id.in_(matching_work_ids))

        if institution_id:
            institution_work_ids = select(AuthorWorkAffiliation.work_id).where(
                AuthorWorkAffiliation.institution_id == institution_id
            )
            statement = statement.where(Work.id.in_(institution_work_ids))

        if topic_id:
            topic_work_ids = select(WorkTopic.work_id).where(
                WorkTopic.topic_id == topic_id
            )
            statement = statement.where(Work.id.in_(topic_work_ids))

        if from_date:
            statement = statement.where(
                (Work.publication_date >= from_date)
                | (
                    Work.publication_date.is_(None)
                    & (Work.publication_year >= from_date.year)
                )
            )
        if to_date:
            statement = statement.where(
                (Work.publication_date <= to_date)
                | (
                    Work.publication_date.is_(None)
                    & (Work.publication_year <= to_date.year)
                )
            )

        statement = statement.order_by(
            Work.publication_date.desc().nulls_last(),
            Work.publication_year.desc().nulls_last(),
            Work.title.asc(),
        )
        return self.db.exec(statement).all()

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

    @staticmethod
    def _normalized_title():
        return func.trim(
            func.regexp_replace(
                func.lower(func.unaccent(Work.title)),
                "[^a-z0-9]+",
                " ",
                "g",
            )
        )

    @staticmethod
    def _list_filters(
        q: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ):
        filters = []
        if q:
            search = f"%{q.lower()}%"
            filters.append(
                (func.unaccent(func.lower(Work.title)).ilike(func.unaccent(search)))
                | (Work.doi.ilike(search))
            )
        if from_date:
            filters.append(
                (Work.publication_date >= from_date)
                | (
                    Work.publication_date.is_(None)
                    & (Work.publication_year >= from_date.year)
                )
            )
        if to_date:
            filters.append(
                (Work.publication_date <= to_date)
                | (
                    Work.publication_date.is_(None)
                    & (Work.publication_year <= to_date.year)
                )
            )
        return filters

    def list_works(
        self,
        q: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        limit: int = 10,
        offset: int = 0,
    ):
        normalized_title = self._normalized_title()
        filters = self._list_filters(q=q, from_date=from_date, to_date=to_date)
        ranked = (
            select(
                Work.id.label("work_id"),
                normalized_title.label("title_key"),
                func.row_number()
                .over(
                    partition_by=normalized_title,
                    order_by=(
                        Work.cited_by_count.desc(),
                        Work.publication_year.desc().nulls_last(),
                        Work.id.asc(),
                    ),
                )
                .label("position"),
            )
            .where(*filters)
            .subquery()
        )

        total_statement = (
            select(func.count())
            .select_from(ranked)
            .where(ranked.c.position == 1)
        )
        total = self.db.exec(total_statement).one()

        representatives_statement = (
            select(Work, ranked.c.title_key)
            .join(ranked, Work.id == ranked.c.work_id)
            .where(ranked.c.position == 1)
            .order_by(
                Work.publication_date.desc().nulls_last(),
                Work.publication_year.desc().nulls_last(),
                Work.title.asc(),
            )
            .offset(offset)
            .limit(limit)
        )
        representatives = self.db.exec(representatives_statement).all()
        title_keys = [title_key for _, title_key in representatives]
        if not title_keys:
            return [], total

        versions_statement = (
            select(Work, normalized_title.label("title_key"))
            .where(*filters)
            .where(normalized_title.in_(title_keys))
            .order_by(
                Work.cited_by_count.desc(),
                Work.publication_year.desc().nulls_last(),
                Work.id.asc(),
            )
        )
        versions_by_title = {}
        for version, title_key in self.db.exec(versions_statement).all():
            versions_by_title.setdefault(title_key, []).append(version)

        items = [
            {
                **representative.model_dump(),
                "versions": versions_by_title.get(title_key, [representative]),
            }
            for representative, title_key in representatives
        ]
        return items, total

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

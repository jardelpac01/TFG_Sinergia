from typing import Optional

from sqlalchemy import case, desc, func, or_, text
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.models import Author, AuthorWork, AuthorWorkAffiliation, Institution, ResearchGroup, Work


class AuthorRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_authors(self, q: Optional[str] = None, limit: int = 50, offset: int = 0):
        statement = select(Author).options(selectinload(Author.research_group))
        count_statement = select(func.count()).select_from(Author)
        if q:
            search = f"%{q.lower()}%"
            condition = (
                func.unaccent(func.lower(Author.display_name)).ilike(func.unaccent(search))
            ) | (Author.orcid.ilike(search))
            statement = statement.where(condition)
            count_statement = count_statement.where(condition)
        total = self.db.exec(count_statement).one()
        statement = (
            statement.outerjoin(ResearchGroup, Author.research_group_id == ResearchGroup.id)
            .order_by(
                case((func.lower(ResearchGroup.name) == "minerva", 0), else_=1),
                Author.display_name.asc(),
            )
            .offset(offset)
            .limit(limit)
        )
        items = self.db.exec(statement).all()
        return items, total

    def get_author(self, author_id: str):
        statement = (
            select(Author)
            .where(Author.id == author_id)
            .options(
                selectinload(Author.topics),
                selectinload(Author.last_known_institution),
                selectinload(Author.research_group),
            )
        )
        return self.db.exec(statement).one_or_none()

    def get_author_works(self, author_id: str):
        statement = (
            select(Work)
            .join(AuthorWork, Work.id == AuthorWork.work_id)
            .where(AuthorWork.author_id == author_id)
            .options(selectinload(Work.authors), selectinload(Work.topics), selectinload(Work.source))
            .order_by(desc(Work.publication_year))
        )
        return self.db.exec(statement).all()

    def _shared_work_ids(self, author_id: str):
        return select(AuthorWork.work_id).where(AuthorWork.author_id == author_id)

    def get_coauthors(self, author_id: str):
        work_ids_subquery = self._shared_work_ids(author_id)
        statement = (
            select(
                Author.id,
                Author.display_name,
                func.count(AuthorWork.work_id).label("shared_works_count"),
            )
            .join(AuthorWork, Author.id == AuthorWork.author_id)
            .where(AuthorWork.work_id.in_(work_ids_subquery))
            .where(Author.id != author_id)
            .group_by(Author.id, Author.display_name)
            .order_by(desc("shared_works_count"))
        )
        return self.db.exec(statement).all()

    def get_author_by_name(self, name: str):
        search = f"%{name.strip().lower()}%"
        alternatives_match = text(
            """
            EXISTS (
                SELECT 1
                FROM jsonb_array_elements_text(
                    COALESCE(authors.display_name_alternatives, '[]'::jsonb)
                ) AS alt(value)
                WHERE unaccent(lower(alt.value)) ILIKE unaccent(:search)
            )
            """
        ).bindparams(search=search)
        statement = (
            select(Author)
            .where(
                or_(
                    func.unaccent(func.lower(Author.display_name)).ilike(func.unaccent(search)),
                    alternatives_match,
                )
            )
            .order_by(Author.display_name.asc())
        )
        return self.db.exec(statement).all()

    def get_coauthors_with_location(self, author_id: str):
        work_ids_subquery = self._shared_work_ids(author_id)
        statement = (
            select(
                Author,
                func.count(func.distinct(AuthorWork.work_id)).label("shared_works_count"),
            )
            .join(AuthorWork, Author.id == AuthorWork.author_id)
            .where(AuthorWork.work_id.in_(work_ids_subquery))
            .where(Author.id != author_id)
            .options(selectinload(Author.last_known_institution))
            .group_by(Author.id)
            .order_by(desc("shared_works_count"))
        )
        return self.db.exec(statement).all()

    def get_country_collaborations(self, author_id: str):
        work_ids_subquery = self._shared_work_ids(author_id)
        statement = (
            select(
                Institution.country_code,
                func.count(func.distinct(AuthorWorkAffiliation.work_id)).label("works_count"),
            )
            .join(Institution, Institution.id == AuthorWorkAffiliation.institution_id)
            .where(AuthorWorkAffiliation.work_id.in_(work_ids_subquery))
            .where(AuthorWorkAffiliation.author_id != author_id)
            .group_by(Institution.country_code)
            .order_by(desc("works_count"))
        )
        return self.db.exec(statement).all()

    def get_city_collaborations(self, author_id: str):
        work_ids_subquery = self._shared_work_ids(author_id)
        statement = (
            select(
                Institution.city,
                Institution.country_code,
                Institution.geo_lat,
                Institution.geo_lon,
                func.count(func.distinct(AuthorWorkAffiliation.author_id)).label("authors_count"),
            )
            .join(Institution, Institution.id == AuthorWorkAffiliation.institution_id)
            .where(AuthorWorkAffiliation.work_id.in_(work_ids_subquery))
            .where(AuthorWorkAffiliation.author_id != author_id)
            .where(Institution.geo_lat.is_not(None))
            .where(Institution.geo_lon.is_not(None))
            .group_by(Institution.city, Institution.country_code, Institution.geo_lat, Institution.geo_lon)
            .order_by(desc("authors_count"))
        )
        return self.db.exec(statement).all()

    def get_works_by_year(self, author_id: str):
        statement = (
            select(Work.publication_year, func.count(func.distinct(Work.id)).label("works_count"))
            .join(AuthorWork, Work.id == AuthorWork.work_id)
            .where(AuthorWork.author_id == author_id)
            .where(Work.publication_year.is_not(None))
            .group_by(Work.publication_year)
            .order_by(Work.publication_year.asc())
        )
        return self.db.exec(statement).all()

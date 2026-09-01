from typing import Optional

from sqlalchemy import desc, func
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.models import Author, AuthorWork, AuthorWorkAffiliation, Institution, Work


class AuthorRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_authors(self, q: Optional[str] = None, limit: int = 50):
        statement = select(Author)
        if q:
            search = f"%{q.lower()}%"
            statement = statement.where(
                (Author.display_name.ilike(search)) | (Author.orcid.ilike(search))
            )
        statement = statement.order_by(Author.display_name.asc()).limit(limit)
        return self.db.exec(statement).all()

    def get_author(self, author_id: str):
        statement = (
            select(Author)
            .where(Author.id == author_id)
            .options(selectinload(Author.topics), selectinload(Author.last_known_institution))
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

    def get_coauthors(self, author_id: str):
        work_ids_subquery = select(AuthorWork.work_id).where(AuthorWork.author_id == author_id)
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

    def get_country_collaborations(self, author_id: str):
        work_ids_subquery = select(AuthorWork.work_id).where(AuthorWork.author_id == author_id)
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

from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.models import Institution, Author


class InstitutionRepository:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _search_condition(q: Optional[str] = None):
        if not q:
            return None
        search = f"%{q.lower()}%"
        return (
            func.unaccent(func.lower(Institution.name)).ilike(func.unaccent(search))
        ) | (Institution.country_code.ilike(search))

    def list_institutions(self, q: Optional[str] = None, limit: int = 50, offset: int = 0):
        statement = select(Institution)
        count_statement = select(func.count()).select_from(Institution)
        condition = self._search_condition(q)
        if condition is not None:
            statement = statement.where(condition)
            count_statement = count_statement.where(condition)
        total = self.db.exec(count_statement).one()
        statement = statement.order_by(Institution.name.asc()).offset(offset).limit(limit)
        items = self.db.exec(statement).all()
        return items, total

    def list_institutions_for_export(self, q: Optional[str] = None):
        statement = select(Institution).options(selectinload(Institution.authors))
        condition = self._search_condition(q)
        if condition is not None:
            statement = statement.where(condition)
        statement = statement.order_by(Institution.name.asc())
        return self.db.exec(statement).all()

    def get_institution(self, institution_id: str) -> Optional[Institution]:
        return self.db.get(Institution, institution_id)

    def get_institution_authors(self, institution_id: str, limit: int = 15, offset: int = 0):
        statement = (
            select(Author)
            .where(Author.last_known_institution_id == institution_id)
            .options(selectinload(Author.research_group))
            .order_by(Author.display_name.asc())
            .offset(offset)
            .limit(limit)
        )
        count_statement = (
            select(func.count())
            .select_from(Author)
            .where(Author.last_known_institution_id == institution_id)
        )
        items = self.db.exec(statement).all()
        total = self.db.exec(count_statement).one()
        return items, total

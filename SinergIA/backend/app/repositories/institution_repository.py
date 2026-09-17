from typing import Optional

from sqlalchemy import func
from sqlmodel import Session, select

from app.models import Institution, Author


class InstitutionRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_institutions(self, q: Optional[str] = None, limit: int = 50, offset: int = 0):
        statement = select(Institution)
        count_statement = select(func.count()).select_from(Institution)
        if q:
            search = f"%{q.lower()}%"
            condition = (
                func.unaccent(func.lower(Institution.name)).ilike(func.unaccent(search))
            ) | (Institution.country_code.ilike(search))
            statement = statement.where(condition)
            count_statement = count_statement.where(condition)
        total = self.db.exec(count_statement).one()
        statement = statement.order_by(Institution.name.asc()).offset(offset).limit(limit)
        items = self.db.exec(statement).all()
        return items, total

    def get_institution(self, institution_id: str) -> Optional[Institution]:
        return self.db.get(Institution, institution_id)

    def get_institution_authors(self, institution_id: str):
        statement = (
            select(Author)
            .where(Author.last_known_institution_id == institution_id)
            .order_by(Author.display_name.asc())
        )
        return self.db.exec(statement).all()

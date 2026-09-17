from typing import Optional

from sqlalchemy import func
from sqlmodel import Session, select

from app.models import Institution, Author


class InstitutionRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_institutions(self, q: Optional[str] = None, limit: int = 50):
        statement = select(Institution)
        if q:
            search = f"%{q.lower()}%"
            statement = statement.where(
                (func.unaccent(func.lower(Institution.name)).ilike(func.unaccent(search)))
                | (Institution.country_code.ilike(search))
            )
        statement = statement.order_by(Institution.name.asc()).limit(limit)
        return self.db.exec(statement).all()

    def get_institution(self, institution_id: str) -> Optional[Institution]:
        return self.db.get(Institution, institution_id)

    def get_institution_authors(self, institution_id: str):
        statement = (
            select(Author)
            .where(Author.last_known_institution_id == institution_id)
            .order_by(Author.display_name.asc())
        )
        return self.db.exec(statement).all()

from typing import Optional

from sqlmodel import Session, select

from app.models import Source


class SourceRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_sources(self, q: Optional[str] = None, limit: int = 50):
        statement = select(Source)
        if q:
            search = f"%{q.lower()}%"
            statement = statement.where(
                (Source.display_name.ilike(search)) | (Source.publisher.ilike(search))
            )
        statement = statement.order_by(Source.display_name.asc()).limit(limit)
        return self.db.exec(statement).all()

    def get_source(self, source_id: str) -> Optional[Source]:
        return self.db.get(Source, source_id)

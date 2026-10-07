from typing import Optional

from sqlalchemy import func
from sqlmodel import Session, select

from app.models import Topic


class TopicRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_topics(self, q: Optional[str] = None, limit: int = 50):
        statement = select(Topic)
        if q:
            search = f"%{q.lower()}%"
            statement = statement.where(
                (func.unaccent(func.lower(Topic.display_name)).ilike(func.unaccent(search)))
                | (func.unaccent(func.lower(Topic.field)).ilike(func.unaccent(search)))
                | (func.unaccent(func.lower(Topic.domain)).ilike(func.unaccent(search)))
            )
        statement = statement.order_by(Topic.display_name.asc()).limit(limit)
        return self.db.exec(statement).all()

    def get_topic(self, topic_id: str) -> Optional[Topic]:
        return self.db.get(Topic, topic_id)

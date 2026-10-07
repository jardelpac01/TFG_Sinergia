from typing import List, Optional

from sqlmodel import Session

from app.models import Topic
from app.repositories.topic_repository import TopicRepository


class TopicService:
    def __init__(self, db: Session):
        self.repository = TopicRepository(db)

    def list_topics(self, q: Optional[str] = None, limit: int = 50) -> List[Topic]:
        return self.repository.list_topics(q=q, limit=limit)

    def get_topic(self, topic_id: str) -> Optional[Topic]:
        return self.repository.get_topic(topic_id)

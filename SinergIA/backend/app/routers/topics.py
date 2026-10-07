from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.database import get_db
from app.schemas.topic import TopicRead
from app.services.topic_service import TopicService


router = APIRouter(prefix="/topics", tags=["topics"])


@router.get("", response_model=List[TopicRead])
def list_topics(
    q: Optional[str] = Query(default=None, description="Search topic by display name or field"),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    service = TopicService(db)
    return service.list_topics(q=q, limit=limit)


@router.get("/{topic_id}", response_model=TopicRead)
def read_topic(topic_id: str, db: Session = Depends(get_db)):
    service = TopicService(db)
    topic = service.get_topic(topic_id)
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

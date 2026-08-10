from sqlmodel import Session, create_engine
from app.config import settings

engine = create_engine(settings.DATABASE_URL, echo=False)


def get_db():
    with Session(engine) as db:
        yield db

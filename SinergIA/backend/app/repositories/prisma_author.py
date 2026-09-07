from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlmodel import select

from app.models import PrismaAuthor


class PrismaAuthorRepository:
    def __init__(self, db: Session):
        self.db = db

    def upsert(self, profile: dict) -> PrismaAuthor:
        existing = self.db.get(PrismaAuthor, profile["prisma_id"])
        if existing is None:
            existing = PrismaAuthor(prisma_id=profile["prisma_id"])
            self.db.add(existing)

        existing.display_name = profile["display_name"]
        existing.department = profile.get("department")
        existing.orcid = profile.get("orcid")
        existing.openalex_author_id = profile.get("openalex_author_id")
        existing.dialnet_code = profile.get("dialnet_code")
        existing.updated_at = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(existing)
        return existing

    def get_by_openalex_id(self, openalex_author_id: str) -> PrismaAuthor | None:
        return self.db.exec(
            select(PrismaAuthor).where(PrismaAuthor.openalex_author_id == openalex_author_id)
        ).first()

    def get_by_orcid(self, orcid: str) -> PrismaAuthor | None:
        return self.db.exec(
            select(PrismaAuthor).where(PrismaAuthor.orcid == orcid)
        ).first()

    def get_all_with_openalex_id(self) -> list[PrismaAuthor]:
        return self.db.exec(
            select(PrismaAuthor).where(PrismaAuthor.openalex_author_id.is_not(None))
        ).all()

from sqlalchemy.orm import Session
from sqlmodel import select

from app.models import (
    Author,
    AuthorTopic,
    AuthorWork,
    AuthorWorkAffiliation,
    Institution,
    Source,
    Topic,
    Work,
    WorkTopic,
)


class IngestionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_author_by_orcid(self, orcid: str):
        return self.db.exec(select(Author).where(Author.orcid == orcid)).first()

    def get_authors_with_display_name(self):
        return self.db.exec(select(Author).where(Author.display_name.is_not(None))).all()

    def get_author(self, author_id: str):
        return self.db.get(Author, author_id)

    def upsert_author(self, author_data: dict, existing_author: Author | None = None):
        author_id = author_data.get("id")
        orcid = author_data.get("orcid")
        display_name = author_data.get("display_name")
        institution_id = author_data.get("last_known_institution_id")
        is_full_profile = "works_count" in author_data

        if existing_author is not None:
            if is_full_profile or not existing_author.display_name or existing_author.display_name == "Unknown":
                if display_name:
                    existing_author.display_name = display_name
            if not existing_author.orcid and orcid:
                existing_author.orcid = orcid
            if author_data.get("h_index") is not None:
                existing_author.h_index = author_data.get("h_index", existing_author.h_index or 0)
            if author_data.get("works_count") is not None:
                existing_author.works_count = author_data.get("works_count", existing_author.works_count or 0)
            if author_data.get("cited_by_count") is not None:
                existing_author.cited_by_count = author_data.get("cited_by_count", existing_author.cited_by_count or 0)
            if "counts_by_year" in author_data and author_data.get("counts_by_year") is not None:
                existing_author.counts_by_year = author_data.get("counts_by_year")
            if institution_id is not None:
                existing_author.last_known_institution_id = institution_id
            self.db.add(existing_author)
            return existing_author.id

        new_author = Author(
            id=author_id,
            display_name=display_name,
            orcid=orcid,
            h_index=author_data.get("h_index", 0),
            works_count=author_data.get("works_count", 0),
            cited_by_count=author_data.get("cited_by_count", 0),
            counts_by_year=author_data.get("counts_by_year", {}),
            last_known_institution_id=institution_id,
        )
        self.db.merge(new_author)
        return author_id

    def upsert_institution(self, inst_data: dict):
        self.db.merge(Institution(
            id=inst_data.get("id"),
            name=inst_data.get("name") or inst_data.get("display_name", "Unknown"),
            country_code=inst_data.get("country_code"),
            ror=inst_data.get("ror"),
            type=inst_data.get("type"),
            geo_lat=inst_data.get("geo_lat"),
            geo_lon=inst_data.get("geo_lon"),
            city=inst_data.get("city"),
        ))

    def upsert_source(self, source_data: dict):
        self.db.merge(Source(
            id=source_data.get("id"),
            display_name=source_data.get("display_name", "Unknown source"),
            issn=source_data.get("issn"),
            publisher=source_data.get("publisher"),
            type=source_data.get("type"),
        ))

    def upsert_topic(self, topic_data: dict):
        self.db.merge(Topic(
            id=topic_data.get("id"),
            display_name=topic_data.get("display_name", "Unknown topic"),
            subfield=topic_data.get("subfield"),
            field=topic_data.get("field"),
            domain=topic_data.get("domain"),
        ))

    def upsert_work(self, work_data: dict):
        self.db.merge(Work(
            id=work_data.get("id"),
            title=work_data.get("title", "Untitled"),
            publication_year=work_data.get("publication_year"),
            publication_date=work_data.get("publication_date"),
            language=work_data.get("language"),
            doi=work_data.get("doi"),
            cited_by_count=work_data.get("cited_by_count", 0),
            is_oa=work_data.get("is_oa", False),
            oa_status=work_data.get("oa_status"),
            is_retracted=work_data.get("is_retracted", False),
            type=work_data.get("type"),
            source_id=work_data.get("source_id"),
        ))

    def add_author_work_relation(self, author_id: str, work_id: str, position: str, is_corr: bool):
        """Creates the bridge relation between Author and Work."""
        self.db.merge(AuthorWork(
            author_id=author_id,
            work_id=work_id,
            author_position=position,
            is_corresponding=is_corr,
        ))

    def add_author_topic_relation(self, author_id: str, topic_id: str, score: float):
        """Creates the relation between Author and Topic."""
        self.db.merge(AuthorTopic(
            author_id=author_id,
            topic_id=topic_id,
            score=score,
        ))

    def add_work_topic_relation(self, work_id: str, topic_id: str, score: float, is_primary: bool):
        """Creates the relation between Work and Topic."""
        self.db.merge(WorkTopic(
            work_id=work_id,
            topic_id=topic_id,
            score=score,
            is_primary=is_primary,
        ))

    def add_author_work_affiliation(self, author_id: str, work_id: str, institution_id: str):
        """Creates the three-way relation between Author, Work and Institution."""
        self.db.merge(AuthorWorkAffiliation(
            author_id=author_id,
            work_id=work_id,
            institution_id=institution_id,
        ))

    def commit(self):
        self.db.commit()
from sqlalchemy.orm import Session

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

    def upsert_author(self, author_data: dict):
        self.db.merge(Author(
            id=author_data.get("id"),
            display_name=author_data.get("display_name"),
            orcid=author_data.get("orcid"),
            h_index=author_data.get("h_index", 0),
            works_count=author_data.get("works_count", 0),
            cited_by_count=author_data.get("cited_by_count", 0),
            counts_by_year=author_data.get("counts_by_year", {}),
            last_known_institution_id=author_data.get("last_known_institution_id"),
        ))

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
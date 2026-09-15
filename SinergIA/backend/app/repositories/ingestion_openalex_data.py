from datetime import datetime, timezone

from sqlalchemy.orm import Session
from sqlmodel import select

from app.models import (
    Author,
    AuthorMergeLog,
    AuthorTopic,
    AuthorWork,
    AuthorWorkAffiliation,
    Institution,
    Source,
    Topic,
    Work,
    WorkReference,
    WorkTopic,
)


class IngestionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_author_by_orcid(self, orcid: str):
        return self.db.exec(select(Author).where(Author.orcid == orcid)).first()

    def get_institution(self, institution_id: str):
        return self.db.get(Institution, institution_id)

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
        display_name_alternatives = author_data.get("display_name_alternatives")

        if existing_author is not None:
            if is_full_profile or not existing_author.display_name or existing_author.display_name == "Unknown":
                if display_name:
                    existing_author.display_name = display_name
            if not existing_author.orcid and orcid:
                existing_author.orcid = orcid
            if display_name_alternatives is not None:
                merged_alternatives = list(
                    dict.fromkeys(
                        [*(existing_author.display_name_alternatives or []), *display_name_alternatives]
                    )
                )
                existing_author.display_name_alternatives = merged_alternatives
            if author_data.get("h_index") is not None:
                existing_author.h_index = author_data.get("h_index", existing_author.h_index or 0)
            if author_data.get("works_count") is not None:
                existing_author.works_count = author_data.get("works_count", existing_author.works_count or 0)
            if author_data.get("cited_by_count") is not None:
                existing_author.cited_by_count = author_data.get("cited_by_count", existing_author.cited_by_count or 0)
            if "counts_by_year" in author_data and author_data.get("counts_by_year") is not None:
                existing_author.counts_by_year = author_data.get("counts_by_year")
            if "raw_data" in author_data and author_data.get("raw_data") is not None:
                existing_author.raw_data = author_data.get("raw_data")
            if institution_id is not None:
                existing_author.last_known_institution_id = institution_id
            existing_author.updated_at = datetime.now(timezone.utc)
            self.db.add(existing_author)
            return existing_author.id

        new_author = Author(
            id=author_id,
            display_name=display_name,
            display_name_alternatives=display_name_alternatives,
            orcid=orcid,
            h_index=author_data.get("h_index", 0),
            works_count=author_data.get("works_count", 0),
            cited_by_count=author_data.get("cited_by_count", 0),
            counts_by_year=author_data.get("counts_by_year", {}),
            raw_data=author_data.get("raw_data"),
            last_known_institution_id=institution_id,
            research_group_id=author_data.get("research_group_id"),
            updated_at=datetime.now(timezone.utc),
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
            homepage_url=inst_data.get("homepage_url"),
            aliases=inst_data.get("aliases"),
            works_count=inst_data.get("works_count") or 0,
            cited_by_count=inst_data.get("cited_by_count") or 0,
            raw_data=inst_data.get("raw_data"),
        ))

    def upsert_source(self, source_data: dict):
        self.db.merge(Source(
            id=source_data.get("id"),
            display_name=source_data.get("display_name", "Unknown source"),
            issn=source_data.get("issn"),
            publisher=source_data.get("publisher"),
            type=source_data.get("type"),
            country_code=source_data.get("country_code"),
            is_oa=source_data.get("is_oa"),
            raw_data=source_data.get("raw_data"),
        ))

    def upsert_topic(self, topic_data: dict):
        self.db.merge(Topic(
            id=topic_data.get("id"),
            display_name=topic_data.get("display_name", "Unknown topic"),
            subfield=topic_data.get("subfield"),
            field=topic_data.get("field"),
            domain=topic_data.get("domain"),
            raw_data=topic_data.get("raw_data"),
        ))

    def upsert_work(self, work_data: dict):
        self.db.merge(Work(
            id=work_data.get("id"),
            title=work_data.get("title", "Untitled"),
            abstract=work_data.get("abstract"),
            publication_year=work_data.get("publication_year"),
            publication_date=work_data.get("publication_date"),
            language=work_data.get("language"),
            doi=work_data.get("doi"),
            cited_by_count=work_data.get("cited_by_count", 0),
            is_oa=work_data.get("is_oa", False),
            oa_status=work_data.get("oa_status"),
            oa_license=work_data.get("oa_license"),
            is_retracted=work_data.get("is_retracted", False),
            type=work_data.get("type"),
            source_id=work_data.get("source_id"),
            raw_data=work_data.get("raw_data"),
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

    def add_author_work_affiliation(self, author_id: str, work_id: str, institution_id: str, raw_affiliation: str | None = None):
        """Creates the three-way relation between Author, Work and Institution."""
        self.db.merge(AuthorWorkAffiliation(
            author_id=author_id,
            work_id=work_id,
            institution_id=institution_id,
            raw_affiliation=raw_affiliation,
        ))

    def add_work_reference(self, work_id: str, referenced_work_id: str):
        """Creates a citation relation: work_id cites referenced_work_id."""
        self.db.merge(WorkReference(
            work_id=work_id,
            referenced_work_id=referenced_work_id,
        ))

    def work_exists(self, work_id: str) -> bool:
        return self.db.get(Work, work_id) is not None

    def add_author_merge_log(
        self,
        incoming_author_id: str,
        incoming_display_name: str,
        matched_author_id: str,
        matched_display_name: str,
        score: float,
        score_breakdown: dict,
    ):
        """Records an automatic heuristic author merge for later auditing."""
        self.db.add(
            AuthorMergeLog(
                incoming_author_id=incoming_author_id,
                incoming_display_name=incoming_display_name,
                matched_author_id=matched_author_id,
                matched_display_name=matched_display_name,
                score=score,
                score_breakdown=score_breakdown,
            )
        )

    def commit(self):
        self.db.commit()
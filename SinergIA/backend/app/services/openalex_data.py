import re
import requests
from sqlalchemy.orm import Session

from app.repositories.ingestion_openalex_data import IngestionRepository


HEADERS = {"User-Agent": "SinergiaTFG/1.0"}
ORCID_REGEX = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")


class OpenAlexService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = IngestionRepository(db)

    def clean_id(self, url: str) -> str | None:
        """Extracts the OpenAlex entity ID from a full URL (e.g. https://openalex.org/A123 → A123)."""
        if not url:
            return None
        return url.split("/")[-1]

    def _fetch_json(self, url: str) -> dict | None:
        response = requests.get(url, headers=HEADERS, timeout=30)
        if response.status_code != 200:
            return None
        return response.json()

    def store_institution(self, institution_data: dict | None) -> str | None:
        """Persists an institution from OpenAlex and returns its normalized ID."""
        if not institution_data:
            return None
        institution_id = self.clean_id(institution_data.get("id"))
        if not institution_id:
            return None
        geo = institution_data.get("geo") or {}
        self.repo.upsert_institution({
            "id": institution_id,
            "display_name": institution_data.get("display_name"),
            "country_code": institution_data.get("country_code"),
            "ror": institution_data.get("ror"),
            "type": institution_data.get("type"),
            "geo_lat": geo.get("latitude"),
            "geo_lon": geo.get("longitude"),
            "city": geo.get("city"),
        })
        return institution_id

    def store_topic(self, topic_data: dict | None) -> str | None:
        """Persists a topic from OpenAlex and returns its normalized ID."""
        if not topic_data:
            return None
        topic_id = self.clean_id(topic_data.get("id"))
        if not topic_id:
            return None
        subfield = topic_data.get("subfield") or {}
        field = topic_data.get("field") or {}
        domain = topic_data.get("domain") or {}
        self.repo.upsert_topic({
            "id": topic_id,
            "display_name": topic_data.get("display_name"),
            "subfield": subfield.get("display_name"),
            "field": field.get("display_name"),
            "domain": domain.get("display_name"),
        })
        return topic_id

    def store_source(self, source_data: dict | None) -> str | None:
        """Persists a source (journal, conference, etc.) from OpenAlex and returns its normalized ID."""
        if not source_data:
            return None
        source_id = self.clean_id(source_data.get("id"))
        if not source_id:
            return None
        issn = source_data.get("issn")
        if isinstance(issn, list):
            issn = issn[0] if issn else None
        self.repo.upsert_source({
            "id": source_id,
            "display_name": source_data.get("display_name"),
            "issn": issn,
            "publisher": source_data.get("host_organization_name") or source_data.get("publisher"),
            "type": source_data.get("type"),
        })
        return source_id

    def fetch_and_store_author(self, orcid: str) -> str | None:
        """
        Validates the ORCID format, fetches the author profile from OpenAlex
        and persists it along with their topics and institution.
        Returns the normalized OpenAlex author ID, or None if not found.
        """
        if not ORCID_REGEX.match(orcid):
            raise ValueError(f"Invalid ORCID format: '{orcid}'. Expected format: 0000-0001-2345-6789")

        url = f"https://api.openalex.org/authors/orcid:{orcid}"
        response = self._fetch_json(url)

        if not response:
            return None

        data = response
        author_id = self.clean_id(data.get("id"))
        if not author_id:
            return None

        inst_id = self.store_institution(data.get("last_known_institution"))

        self.repo.upsert_author({
            "id": author_id,
            "display_name": data.get("display_name"),
            "orcid": data.get("orcid"),
            "h_index": data.get("summary_stats", {}).get("h_index", 0),
            "works_count": data.get("works_count", 0),
            "cited_by_count": data.get("cited_by_count", 0),
            "counts_by_year": data.get("counts_by_year", []),
            "last_known_institution_id": inst_id,
        })

        for topic_data in data.get("topics", []):
            topic_id = self.store_topic(topic_data)
            if topic_id:
                self.repo.add_author_topic_relation(
                    author_id=author_id,
                    topic_id=topic_id,
                    score=float(topic_data.get("score", 0.0) or 0.0),
                )

        self.repo.commit()
        self.fetch_and_store_works(author_id)
        return author_id

    def fetch_and_store_works(self, author_openalex_id: str):
        """
        Fetches all works for a given OpenAlex author ID using cursor-based pagination
        and persists each work along with its topics, co-authors and affiliations.
        """
        cursor = "*"

        while cursor:
            url = (
                f"https://api.openalex.org/works"
                f"?filter=author.id:{author_openalex_id}&cursor={cursor}"
            )
            response = self._fetch_json(url)
            if not response:
                break

            data = response

            for work_data in data.get("results", []):
                work_id = self.clean_id(work_data.get("id"))
                if not work_id:
                    continue

                primary_location = work_data.get("primary_location") or {}
                source_id = self.store_source(primary_location.get("source"))

                self.repo.upsert_work({
                    "id": work_id,
                    "title": work_data.get("title"),
                    "publication_year": work_data.get("publication_year"),
                    "publication_date": work_data.get("publication_date"),
                    "language": work_data.get("language"),
                    "doi": work_data.get("doi"),
                    "cited_by_count": work_data.get("cited_by_count", 0),
                    "is_oa": work_data.get("open_access", {}).get("is_oa", False),
                    "oa_status": work_data.get("open_access", {}).get("oa_status"),
                    "is_retracted": work_data.get("is_retracted", False),
                    "type": work_data.get("type"),
                    "source_id": source_id,
                })

                # Store topics associated with this work
                work_topics = work_data.get("topics", [])
                primary_topic_id = self.clean_id(
                    (work_data.get("primary_topic") or {}).get("id")
                )

                for topic_data in work_topics:
                    topic_id = self.store_topic(topic_data)
                    if topic_id:
                        self.repo.add_work_topic_relation(
                            work_id=work_id,
                            topic_id=topic_id,
                            score=float(topic_data.get("score", 0.0) or 0.0),
                            is_primary=(topic_id == primary_topic_id),
                        )

                # If the primary topic is not included in the topics list, store it separately
                if primary_topic_id and not any(
                    self.clean_id(t.get("id")) == primary_topic_id for t in work_topics
                ):
                    primary_topic = work_data.get("primary_topic") or {}
                    topic_id = self.store_topic(primary_topic)
                    if topic_id:
                        self.repo.add_work_topic_relation(
                            work_id=work_id,
                            topic_id=topic_id,
                            score=float(primary_topic.get("score", 0.0) or 0.0),
                            is_primary=True,
                        )

                # Store authorships and institutional affiliations for each co-author
                for authorship in work_data.get("authorships", []):
                    author_data = authorship.get("author") or {}
                    authorship_author_id = self.clean_id(author_data.get("id"))
                    if not authorship_author_id:
                        continue

                    # Preserve the main author record and only upsert real co-authors.
                    if authorship_author_id != author_openalex_id:
                        self.repo.upsert_author({
                            "id": authorship_author_id,
                            "display_name": author_data.get("display_name"),
                            "orcid": author_data.get("orcid"),
                        })

                    self.repo.add_author_work_relation(
                        author_id=authorship_author_id,
                        work_id=work_id,
                        position=authorship.get("author_position"),
                        is_corr=authorship.get("is_corresponding", False),
                    )

                    for institution_data in authorship.get("institutions", []):
                        institution_id = self.store_institution(institution_data)
                        if institution_id:
                            self.repo.add_author_work_affiliation(
                                author_id=authorship_author_id,
                                work_id=work_id,
                                institution_id=institution_id,
                            )

            self.repo.commit()
            cursor = data.get("meta", {}).get("next_cursor")

    def fetch_and_store_author_by_identifier(self, author_identifier: str) -> str | None:
        """Fetches an author by ORCID, OpenAlex ID or OpenAlex URL."""
        if ORCID_REGEX.match(author_identifier):
            return self.fetch_and_store_author(author_identifier)

        author_id = self.clean_id(author_identifier)
        if not author_id:
            return None

        data = self._fetch_json(f"https://api.openalex.org/authors/{author_id}")
        if not data:
            return None

        author_id = self.clean_id(data.get("id"))
        if not author_id:
            return None

        inst_id = self.store_institution(data.get("last_known_institution"))

        self.repo.upsert_author({
            "id": author_id,
            "display_name": data.get("display_name"),
            "orcid": data.get("orcid"),
            "h_index": data.get("summary_stats", {}).get("h_index", 0),
            "works_count": data.get("works_count", 0),
            "cited_by_count": data.get("cited_by_count", 0),
            "counts_by_year": data.get("counts_by_year", []),
            "last_known_institution_id": inst_id,
        })

        for topic_data in data.get("topics", []):
            topic_id = self.store_topic(topic_data)
            if topic_id:
                self.repo.add_author_topic_relation(
                    author_id=author_id,
                    topic_id=topic_id,
                    score=float(topic_data.get("score", 0.0) or 0.0),
                )

        self.repo.commit()
        self.fetch_and_store_works(author_id)
        return author_id

    def fetch_and_store_work_by_identifier(self, work_identifier: str) -> str | None:
        """Fetches a single work by OpenAlex ID or URL and persists it."""
        work_id = self.clean_id(work_identifier)
        if not work_id:
            return None

        data = self._fetch_json(f"https://api.openalex.org/works/{work_id}")
        if not data:
            return None

        work_id = self.clean_id(data.get("id"))
        if not work_id:
            return None

        primary_location = data.get("primary_location") or {}
        source_id = self.store_source(primary_location.get("source"))

        self.repo.upsert_work({
            "id": work_id,
            "title": data.get("title"),
            "publication_year": data.get("publication_year"),
            "publication_date": data.get("publication_date"),
            "language": data.get("language"),
            "doi": data.get("doi"),
            "cited_by_count": data.get("cited_by_count", 0),
            "is_oa": data.get("open_access", {}).get("is_oa", False),
            "oa_status": data.get("open_access", {}).get("oa_status"),
            "is_retracted": data.get("is_retracted", False),
            "type": data.get("type"),
            "source_id": source_id,
        })

        work_topics = data.get("topics", [])
        primary_topic_id = self.clean_id((data.get("primary_topic") or {}).get("id"))

        for topic_data in work_topics:
            topic_id = self.store_topic(topic_data)
            if topic_id:
                self.repo.add_work_topic_relation(
                    work_id=work_id,
                    topic_id=topic_id,
                    score=float(topic_data.get("score", 0.0) or 0.0),
                    is_primary=(topic_id == primary_topic_id),
                )

        if primary_topic_id and not any(
            self.clean_id(topic.get("id")) == primary_topic_id for topic in work_topics
        ):
            primary_topic = data.get("primary_topic") or {}
            topic_id = self.store_topic(primary_topic)
            if topic_id:
                self.repo.add_work_topic_relation(
                    work_id=work_id,
                    topic_id=topic_id,
                    score=float(primary_topic.get("score", 0.0) or 0.0),
                    is_primary=True,
                )

        for authorship in data.get("authorships", []):
            author_data = authorship.get("author") or {}
            authorship_author_id = self.clean_id(author_data.get("id"))
            if not authorship_author_id:
                continue

            # Keep the main author record intact and only upsert true co-authors.
            if authorship_author_id != self.clean_id(data.get("id")):
                self.repo.upsert_author({
                    "id": authorship_author_id,
                    "display_name": author_data.get("display_name"),
                    "orcid": author_data.get("orcid"),
                })

            self.repo.add_author_work_relation(
                author_id=authorship_author_id,
                work_id=work_id,
                position=authorship.get("author_position"),
                is_corr=authorship.get("is_corresponding", False),
            )

            for institution_data in authorship.get("institutions", []):
                institution_id = self.store_institution(institution_data)
                if institution_id:
                    self.repo.add_author_work_affiliation(
                        author_id=authorship_author_id,
                        work_id=work_id,
                        institution_id=institution_id,
                    )

        self.repo.commit()
        return work_id
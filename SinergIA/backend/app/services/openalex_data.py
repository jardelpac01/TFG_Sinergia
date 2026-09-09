import re
from collections.abc import Callable
from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.repositories.ingestion_openalex_data import IngestionRepository
from app.schemas.openalex_ingestion import (
    OpenAlexAuthorsBatchIngestItem,
    OpenAlexAuthorsBatchIngestResponse,
)
from app.services.author_identity import AuthorIdentityService
from app.services.http_client import fetch_with_retries


ORCID_REGEX = re.compile(r"^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$")


class OpenAlexUpstreamError(Exception):
    """Raised when OpenAlex cannot be reached or returns a non-recoverable error."""


class AuthorNotFoundError(Exception):
    """Raised when no author can be found in OpenAlex for a given identifier."""


class WorkNotFoundError(Exception):
    """Raised when no work can be found in OpenAlex for a given identifier."""


@dataclass
class AuthorSearchAndIngestResult:

    status: str
    total_results: int
    selected_by: str | None = None
    author_id: str | None = None
    candidates: list[dict] = field(default_factory=list)


class OpenAlexService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = IngestionRepository(db)
        self.author_identity = AuthorIdentityService()

    def upsert_author(self, author_data: dict) -> str | None:
        author_data = self.author_identity.prepare_author_data(author_data)
        orcid = author_data["orcid"]
        existing_author = self.repo.get_author_by_orcid(orcid) if orcid else None
        if existing_author is None:
            existing_author = self.author_identity.find_matching_author(
                display_name=author_data["display_name"],
                institution_id=author_data.get("last_known_institution_id"),
                candidates=self.repo.get_authors_with_display_name(),
                orcid=orcid,
            )
        if existing_author is None and author_data.get("id"):
            existing_author = self.repo.get_author(author_data["id"])
        return self.repo.upsert_author(author_data, existing_author)

    def clean_id(self, url: str) -> str | None:
        """Extracts the OpenAlex entity ID from a full URL (e.g. https://openalex.org/A123 → A123)."""
        if not url:
            return None
        return url.split("/")[-1]

    def _fetch_json(
        self,
        url: str,
        params: dict | None = None,
        max_attempts: int = 4,
        backoff_seconds: float = 1.0,
    ) -> dict | None:
        response = fetch_with_retries(
            url,
            on_error=OpenAlexUpstreamError,
            params=params,
            max_attempts=max_attempts,
            backoff_seconds=backoff_seconds,
        )

        if response.status_code == 200:
            return response.json()

        if response.status_code == 404:
            return None

        raise OpenAlexUpstreamError(
            f"OpenAlex returned unexpected status {response.status_code}."
        )

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

    def search_authors_by_name(self, name: str, page: int = 1, per_page: int = 10) -> tuple[int, list[dict]]:
        """Searches OpenAlex authors by name and returns normalized candidates."""
        data = self._fetch_json(
            "https://api.openalex.org/authors",
            params={"search": name, "page": page, "per-page": per_page},
        )
        if not data:
            return 0, []

        items: list[dict] = []
        for author_data in data.get("results", []):
            openalex_id = self.clean_id(author_data.get("id"))
            if not openalex_id:
                continue

            last_known_institution = author_data.get("last_known_institution") or {}
            display_name_alternatives = [
                str(value).strip()
                for value in (author_data.get("display_name_alternatives") or [])
                if str(value).strip()
            ]
            items.append(
                {
                    "openalex_id": openalex_id,
                    "display_name": author_data.get("display_name") or "Unknown",
                    "display_name_alternatives": display_name_alternatives,
                    "orcid": author_data.get("orcid"),
                    "works_count": int(author_data.get("works_count", 0) or 0),
                    "cited_by_count": int(author_data.get("cited_by_count", 0) or 0),
                    "last_known_institution": last_known_institution.get("display_name"),
                }
            )

        total_results = int((data.get("meta") or {}).get("count", 0) or 0)
        return total_results, items

    def search_and_ingest_author_by_name(
        self, name: str, force: bool = False, per_page: int = 10
    ) -> AuthorSearchAndIngestResult:
        """Searches authors by name and ingests only safe matches unless force is enabled."""
        total_results, candidates = self.search_authors_by_name(name=name, page=1, per_page=per_page)

        if not candidates:
            return AuthorSearchAndIngestResult(status="not_found", total_results=total_results, candidates=[])

        normalized_name = name.strip().casefold()
        exact_matches = [
            candidate
            for candidate in candidates
            if (candidate.get("display_name") or "").strip().casefold() == normalized_name
            or normalized_name in {
                alternative.strip().casefold()
                for alternative in candidate.get("display_name_alternatives", [])
            }
        ]

        selected_candidate = None
        selected_by = None

        if len(exact_matches) == 1:
            selected_candidate = exact_matches[0]
            selected_by = "exact_name_or_alternative_match"
        elif len(candidates) == 1:
            selected_candidate = candidates[0]
            selected_by = "single_result"
        elif force:
            selected_candidate = candidates[0]
            selected_by = "forced_first_result"
        else:
            return AuthorSearchAndIngestResult(
                status="ambiguous",
                total_results=total_results,
                selected_by=None,
                candidates=candidates,
            )

        author_id = self.fetch_and_store_author_by_identifier(selected_candidate["openalex_id"])
        if not author_id:
            return AuthorSearchAndIngestResult(
                status="not_found",
                total_results=total_results,
                selected_by=selected_by,
                candidates=candidates,
            )

        return AuthorSearchAndIngestResult(
            status="ingested",
            author_id=author_id,
            selected_by=selected_by,
            total_results=total_results,
            candidates=candidates,
        )

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

        author_id = self.upsert_author({
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

                    authorship_institution_ids = [
                        institution_id
                        for institution_id in (
                            self.store_institution(institution_data)
                            for institution_data in authorship.get("institutions", [])
                        )
                        if institution_id
                    ]

                    # Preserve the main author record and only upsert real co-authors.
                    if authorship_author_id != author_openalex_id:
                        authorship_author_id = self.upsert_author({
                            "id": authorship_author_id,
                            "display_name": author_data.get("display_name"),
                            "orcid": author_data.get("orcid"),
                            "last_known_institution_id": (
                                authorship_institution_ids[0] if authorship_institution_ids else None
                            ),
                        })

                    self.repo.add_author_work_relation(
                        author_id=authorship_author_id,
                        work_id=work_id,
                        position=authorship.get("author_position"),
                        is_corr=authorship.get("is_corresponding", False),
                    )

                    for institution_id in authorship_institution_ids:
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

        author_id = self.upsert_author({
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

            authorship_institution_ids = [
                institution_id
                for institution_id in (
                    self.store_institution(institution_data)
                    for institution_data in authorship.get("institutions", [])
                )
                if institution_id
            ]

            # Keep the main author record intact and only upsert true co-authors.
            if authorship_author_id != self.clean_id(data.get("id")):
                authorship_author_id = self.upsert_author({
                    "id": authorship_author_id,
                    "display_name": author_data.get("display_name"),
                    "orcid": author_data.get("orcid"),
                    "last_known_institution_id": (
                        authorship_institution_ids[0] if authorship_institution_ids else None
                    ),
                })

            self.repo.add_author_work_relation(
                author_id=authorship_author_id,
                work_id=work_id,
                position=authorship.get("author_position"),
                is_corr=authorship.get("is_corresponding", False),
            )

            for institution_id in authorship_institution_ids:
                self.repo.add_author_work_affiliation(
                    author_id=authorship_author_id,
                    work_id=work_id,
                    institution_id=institution_id,
                )

        self.repo.commit()
        return work_id

    def fetch_and_store_author_or_raise(self, author_identifier: str) -> str:
        """Same as fetch_and_store_author_by_identifier, but raises AuthorNotFoundError
        instead of returning None when no author is found.
        """
        author_id = self.fetch_and_store_author_by_identifier(author_identifier)
        if not author_id:
            raise AuthorNotFoundError(f"No author was found for identifier {author_identifier}.")
        return author_id

    def fetch_and_store_work_or_raise(self, work_identifier: str) -> str:
        """Same as fetch_and_store_work_by_identifier, but raises WorkNotFoundError
        instead of returning None when no work is found.
        """
        work_id = self.fetch_and_store_work_by_identifier(work_identifier)
        if not work_id:
            raise WorkNotFoundError(f"No work was found for identifier {work_identifier}.")
        return work_id

    def ingest_authors_batch(
        self,
        identifiers: list[str],
        ingest_author: Callable[[str], str | None],
        empty_identifier_message: str,
        not_found_message: str,
    ) -> OpenAlexAuthorsBatchIngestResponse:
        """Ingests a batch of author identifiers (ORCIDs or OpenAlex identifiers),
        collecting per-item successes and failures instead of failing the whole batch.
        """
        results: list[OpenAlexAuthorsBatchIngestItem] = []
        ingested = 0
        failed = 0

        for raw_identifier in identifiers:
            identifier = raw_identifier.strip()
            if not identifier:
                failed += 1
                results.append(
                    OpenAlexAuthorsBatchIngestItem(
                        identifier=raw_identifier,
                        status="failed",
                        error=empty_identifier_message,
                    )
                )
                continue

            try:
                author_id = ingest_author(identifier)
            except (ValueError, OpenAlexUpstreamError) as exc:
                failed += 1
                results.append(
                    OpenAlexAuthorsBatchIngestItem(
                        identifier=identifier,
                        status="failed",
                        error=str(exc),
                    )
                )
                continue

            if not author_id:
                failed += 1
                results.append(
                    OpenAlexAuthorsBatchIngestItem(
                        identifier=identifier,
                        status="failed",
                        error=not_found_message,
                    )
                )
                continue

            ingested += 1
            results.append(
                OpenAlexAuthorsBatchIngestItem(
                    identifier=identifier,
                    status="ingested",
                    author_id=author_id,
                )
            )

        return OpenAlexAuthorsBatchIngestResponse(
            requested=len(identifiers),
            ingested=ingested,
            failed=failed,
            results=results,
        )
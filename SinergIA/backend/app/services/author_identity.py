import re
import unicodedata
from typing import Iterable, Optional

from app.models import Author

# Below this score, two authors are never considered the same person.
MATCH_THRESHOLD = 80
# Between this score and MATCH_THRESHOLD, an institution match is required
# to accept the merge (weaker evidence, needs corroboration).
WEAK_MATCH_THRESHOLD = 40

ORCID_BARE_REGEX = re.compile(r"(\d{4}-\d{4}-\d{4}-\d{3}[\dX])", re.IGNORECASE)


class AuthorMatchResult:
    def __init__(self, author: Optional[Author], score: float, breakdown: dict):
        self.author = author
        self.score = score
        self.breakdown = breakdown


class AuthorIdentityService:
    def canonicalize_display_name(self, display_name: str | None) -> str | None:
        if display_name is None:
            return None
        value = display_name.strip()
        return value or None

    def canonicalize_orcid(self, orcid: str | None) -> str | None:
        if not orcid:
            return None
        match = ORCID_BARE_REGEX.search(orcid.strip())
        return f"https://orcid.org/{match.group(1).upper()}" if match else None

    def prepare_author_data(self, author_data: dict) -> dict:
        raw_data = author_data.get("raw_data") or {}
        alternatives = author_data.get("display_name_alternatives")
        if alternatives is None:
            alternatives = raw_data.get("display_name_alternatives")
        normalized_alternatives = [
            str(value).strip()
            for value in (alternatives or [])
            if str(value).strip()
        ]
        return {
            **author_data,
            "display_name": self.canonicalize_display_name(author_data.get("display_name")) or "Unknown",
            "orcid": self.canonicalize_orcid(author_data.get("orcid")),
            "display_name_alternatives": normalized_alternatives,
        }

    def find_matching_author(
        self,
        display_name: str,
        institution_id: str | None,
        candidates: Iterable[Author],
        orcid: str | None = None,
        topic_ids: Iterable[str] | None = None,
        display_name_alternatives: Iterable[str] | None = None,
    ) -> AuthorMatchResult:
        normalized_name = self._normalize_author_name(display_name)
        topic_id_set = set(topic_ids or [])
        incoming_name_variants = {normalized_name} | {
            self._normalize_author_name(alt) for alt in (display_name_alternatives or [])
        }
        incoming_name_variants.discard(None)
        if not normalized_name:
            return AuthorMatchResult(None, 0, {})

        best_candidate = None
        best_score = -1
        best_breakdown: dict = {}
        for candidate in candidates:
            candidate_name = candidate.display_name
            candidate_normalized = self._normalize_author_name(candidate_name)
            if not candidate_normalized:
                continue
            candidate_name_variants = {candidate_normalized} | {
                self._normalize_author_name(alt) for alt in (candidate.display_name_alternatives or [])
            }
            candidate_name_variants.discard(None)

            breakdown = {}
            score = 0
            if institution_id and candidate.last_known_institution_id == institution_id:
                breakdown["same_institution"] = 50
                score += 50
            if incoming_name_variants & candidate_name_variants:
                breakdown["known_alias_match"] = 90
                score += 90
            elif candidate_normalized == normalized_name:
                breakdown["exact_name_match"] = 80
                score += 80
            elif self._name_contains_other(candidate_normalized, normalized_name):
                breakdown["name_substring_match"] = 30
                score += 30
            if self._authors_have_same_identity(candidate_name, display_name):
                breakdown["same_surname_family"] = 40
                score += 40
            shared_topics = self._shared_topic_count(candidate, topic_id_set)
            if shared_topics:
                topic_bonus = min(shared_topics * 10, 30)
                breakdown["shared_topics"] = topic_bonus
                breakdown["shared_topics_count"] = shared_topics
                score += topic_bonus

            if score > best_score:
                best_candidate = candidate
                best_score = score
                best_breakdown = breakdown

        if best_score >= MATCH_THRESHOLD:
            return AuthorMatchResult(best_candidate, best_score, best_breakdown)
        if (
            best_score >= WEAK_MATCH_THRESHOLD
            and institution_id
            and best_candidate
            and best_candidate.last_known_institution_id == institution_id
        ):
            return AuthorMatchResult(best_candidate, best_score, best_breakdown)
        return AuthorMatchResult(None, best_score, best_breakdown)

    def match_via_prisma_researchers_by_name(
        self,
        display_name: str | None,
        display_name_alternatives: Iterable[str] | None,
        prisma_authors: Iterable,
    ):
        if not display_name:
            return None
        incoming_variants = {self._normalize_author_name(display_name)} | {
            self._normalize_author_name(alt) for alt in (display_name_alternatives or [])
        }
        incoming_variants.discard(None)
        if not incoming_variants:
            return None

        matches = {}
        for prisma_author in prisma_authors:
            if not prisma_author.openalex_author_id:
                continue
            prisma_normalized = self._normalize_author_name(prisma_author.display_name)
            if not prisma_normalized:
                continue
            is_match = prisma_normalized in incoming_variants or any(
                self._authors_have_same_identity(prisma_author.display_name, variant)
                for variant in (display_name, *(display_name_alternatives or []))
            )
            if is_match:
                matches[prisma_author.openalex_author_id] = prisma_author

        if len(matches) == 1:
            return next(iter(matches.values()))
        return None

    def _name_contains_other(self, left_normalized: str, right_normalized: str) -> bool:
        """True when one full name is a whole-token subset of the other.

        E.g. "isabel nepomuceno" is contained in
        "isabel a nepomuceno chamorro" (all tokens of the shorter name appear,
        in order, within the longer one), which is a much weaker signal than
        an exact match and must be combined with other evidence to merge.
        """
        left_tokens = left_normalized.split()
        right_tokens = right_normalized.split()
        if not left_tokens or not right_tokens:
            return False
        shorter, longer = (
            (left_tokens, right_tokens)
            if len(left_tokens) <= len(right_tokens)
            else (right_tokens, left_tokens)
        )
        if len(shorter) < 2:
            return False
        return " ".join(shorter) in " ".join(longer)

    def _shared_topic_count(self, candidate: Author, topic_id_set: set[str]) -> int:
        if not topic_id_set:
            return 0
        candidate_topic_ids = {topic.id for topic in (candidate.topics or [])}
        return len(candidate_topic_ids & topic_id_set)

    def _normalize_author_name(self, display_name: str | None) -> str | None:
        canonical_name = self.canonicalize_display_name(display_name)
        if canonical_name is None:
            return None

        normalized = unicodedata.normalize("NFKD", canonical_name)
        normalized = normalized.encode("ascii", "ignore").decode("ascii")
        normalized = normalized.lower()
        normalized = re.sub(r"[._-]", " ", normalized)
        normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
        normalized = re.sub(r"\s+", " ", normalized).strip()
        return normalized or None

    def _authors_have_same_identity(self, left_name: str | None, right_name: str | None) -> bool:
        left_normalized = self._normalize_author_name(left_name)
        right_normalized = self._normalize_author_name(right_name)
        if not left_normalized or not right_normalized:
            return False
        if left_normalized == right_normalized:
            return True

        left_tokens = left_normalized.split()
        right_tokens = right_normalized.split()
        if len(left_tokens) < 2 or len(right_tokens) < 2:
            return False
        if not self._given_names_compatible(left_tokens[0], right_tokens[0]):
            return False

        ignored_tokens = {"a", "an", "de", "del", "la", "las", "los", "el", "al", "y"}

        def surname_tokens(tokens: list[str]) -> set[str]:
            surname = [token for token in tokens[1:] if token not in ignored_tokens]
            return set(surname or tokens[1:])

        return bool(surname_tokens(left_tokens) & surname_tokens(right_tokens))

    def _given_names_compatible(self, left_first: str, right_first: str) -> bool:
        """True when the first tokens can plausibly refer to the same given name.

        Handles abbreviations such as "M." for "María": if either token is a
        single letter (an initial), it only needs to match the first letter
        of the other token instead of requiring an exact match.
        """
        if left_first == right_first:
            return True
        if len(left_first) == 1 or len(right_first) == 1:
            return left_first[0] == right_first[0]
        return False

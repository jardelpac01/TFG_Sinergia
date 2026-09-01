import re
import unicodedata
from typing import Iterable, Optional

from app.models import Author


class AuthorIdentityService:
    def canonicalize_display_name(self, display_name: str | None) -> str | None:
        if display_name is None:
            return None
        value = display_name.strip()
        return value or None

    def prepare_author_data(self, author_data: dict) -> dict:
        return {
            **author_data,
            "display_name": self.canonicalize_display_name(author_data.get("display_name")) or "Unknown",
            "orcid": (author_data.get("orcid") or "").strip() or None,
        }

    def find_matching_author(
        self,
        display_name: str,
        institution_id: str | None,
        candidates: Iterable[Author],
        orcid: str | None = None,
    ) -> Optional[Author]:
        normalized_name = self._normalize_author_name(display_name)
        if not normalized_name:
            return None

        best_candidate = None
        best_score = -1
        for candidate in candidates:
            candidate_name = candidate.display_name
            candidate_normalized = self._normalize_author_name(candidate_name)
            if not candidate_normalized:
                continue

            score = 0
            if candidate.orcid and not orcid:
                score += 100
            if institution_id and candidate.last_known_institution_id == institution_id:
                score += 50
            if candidate_normalized == normalized_name:
                score += 80
            if self._authors_have_same_identity(candidate_name, display_name):
                score += 40

            if score > best_score:
                best_candidate = candidate
                best_score = score

        if best_score >= 80:
            return best_candidate
        if (
            best_score >= 40
            and institution_id
            and best_candidate
            and best_candidate.last_known_institution_id == institution_id
        ):
            return best_candidate
        return None

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
        if len(left_tokens) < 2 or len(right_tokens) < 2 or left_tokens[0] != right_tokens[0]:
            return False

        ignored_tokens = {"a", "an", "de", "del", "la", "las", "los", "el", "al", "y"}

        def surname_tokens(tokens: list[str]) -> set[str]:
            surname = [token for token in tokens[1:] if token not in ignored_tokens]
            return set(surname or tokens[1:])

        return bool(surname_tokens(left_tokens) & surname_tokens(right_tokens))

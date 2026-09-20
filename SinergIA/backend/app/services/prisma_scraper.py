import re
import time

from app.services.http_client import fetch_with_retries

BASE_URL = "https://prisma.us.es"

PROFILE_LINK_RE = re.compile(r"investigador/(\d+)")
NAME_RE = re.compile(r'<h1[^>]*id="nombre"[^>]*>(.*?)</h1>', re.DOTALL)
DEPARTMENT_RE = re.compile(
    r"departamento/([A-Za-z0-9]+)\"[^>]*>\s*([^<]+?)\s*</a>", re.DOTALL
)
RESEARCH_GROUP_RE = re.compile(
    r'href="[^"]*/colectivo/grupo/([^"/?#]+)"[^>]*>(.*?)</a>',
    re.DOTALL | re.IGNORECASE,
)
ORCID_RE = re.compile(r"orcid\.org/([0-9Xx\-]+)")
OPENALEX_RE = re.compile(r"openalex\.org/authors/([A-Za-z0-9]+)")
DIALNET_RE = re.compile(r"dialnet\.unirioja\.es/servlet/autor\?codigo=(\d+)")
TAG_RE = re.compile(r"<[^>]+>")
WHITESPACE_RE = re.compile(r"\s+")


class PrismaScraperError(Exception):
    """Raised when Prisma cannot be reached or returns a non-recoverable error."""


def _fetch_html(url: str, max_attempts: int = 4, backoff_seconds: float = 1.0) -> str:
    response = fetch_with_retries(
        url,
        on_error=PrismaScraperError,
        max_attempts=max_attempts,
        backoff_seconds=backoff_seconds,
    )

    if response.status_code == 200:
        return response.text

    raise PrismaScraperError(f"Prisma returned status {response.status_code} for {url}")


def _clean_text(value: str) -> str:
    value = value.replace("&nbsp;", " ")
    value = TAG_RE.sub(" ", value)
    return WHITESPACE_RE.sub(" ", value).strip()


def list_researcher_ids_by_department(department_code: str) -> list[int]:
    """Returns all Prisma investigator IDs listed for a department (e.g. "I0A3")."""
    url = f"{BASE_URL}/investigador/buscar/departamento/{department_code}"
    html = _fetch_html(url)
    ids = {int(match) for match in PROFILE_LINK_RE.findall(html)}
    return sorted(ids)


def fetch_researcher_profile(prisma_id: int) -> dict | None:
    url = f"{BASE_URL}/investigador/{prisma_id}"
    html = _fetch_html(url)

    name_match = NAME_RE.search(html)
    if not name_match:
        return None
    display_name = _clean_text(name_match.group(1))
    if not display_name:
        return None

    department_match = DEPARTMENT_RE.search(html)
    department = _clean_text(department_match.group(2)) if department_match else None

    research_group_match = RESEARCH_GROUP_RE.search(html)
    research_group_code = research_group_match.group(1) if research_group_match else None
    research_group_name = (
        _clean_text(research_group_match.group(2)) if research_group_match else None
    )

    orcid_match = ORCID_RE.search(html)
    orcid = orcid_match.group(1) if orcid_match else None

    openalex_match = OPENALEX_RE.search(html)
    openalex_author_id = openalex_match.group(1) if openalex_match else None

    dialnet_match = DIALNET_RE.search(html)
    dialnet_code = dialnet_match.group(1) if dialnet_match else None

    return {
        "prisma_id": prisma_id,
        "display_name": display_name,
        "department": department,
        "research_group_code": research_group_code,
        "research_group_name": research_group_name,
        "orcid": orcid,
        "openalex_author_id": openalex_author_id,
        "dialnet_code": dialnet_code,
    }


def fetch_department_profiles(department_code: str, delay_seconds: float = 0.3) -> list[dict]:
    """Fetches all researcher profiles for a department, skipping unreadable ones."""
    profiles = []
    for prisma_id in list_researcher_ids_by_department(department_code):
        profile = fetch_researcher_profile(prisma_id)
        if profile is not None:
            profiles.append(profile)
        time.sleep(delay_seconds)
    return profiles

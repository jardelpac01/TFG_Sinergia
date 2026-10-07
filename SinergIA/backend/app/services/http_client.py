"""Shared HTTP fetching helper with retry/backoff logic.

Used by services that call third-party HTTP APIs or scrape external pages
(OpenAlex, Prisma), so the retry policy, headers and retryable status codes
are defined in a single place. Callers remain responsible for interpreting
non-retryable status codes (e.g. treating 404 or other statuses), since that
behavior differs between callers.
"""

import time
from typing import Callable

import requests


HEADERS = {"User-Agent": "SinergiaTFG/1.0"}
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}


def fetch_with_retries(
    url: str,
    on_error: Callable[[str], Exception],
    params: dict | None = None,
    max_attempts: int = 4,
    backoff_seconds: float = 1.0,
    timeout: int = 30,
) -> requests.Response:
    """Performs a GET request, retrying on connection errors and on
    retryable status codes with a linear backoff. Returns the response as
    soon as a non-retryable status is reached (including non-200 statuses
    such as 404), leaving status interpretation to the caller. Raises the
    exception built by `on_error(message)` once retries are exhausted.
    """
    attempt = 1
    while attempt <= max_attempts:
        try:
            response = requests.get(url, headers=HEADERS, params=params, timeout=timeout)
        except requests.RequestException as exc:
            if attempt == max_attempts:
                raise on_error(
                    f"Request failed after {max_attempts} attempts for {url}: {exc}"
                ) from exc
            time.sleep(backoff_seconds * attempt)
            attempt += 1
            continue

        if response.status_code in RETRYABLE_STATUS_CODES:
            if attempt == max_attempts:
                raise on_error(
                    f"Temporary error {response.status_code} after {max_attempts} attempts for {url}."
                )
            time.sleep(backoff_seconds * attempt)
            attempt += 1
            continue

        return response

    raise on_error(f"Request failed for {url}.")

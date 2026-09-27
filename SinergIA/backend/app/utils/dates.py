from calendar import monthrange
from datetime import date
from typing import Optional


def month_start(value: Optional[str]) -> Optional[date]:
    """Parses a "YYYY-MM" string into the first day of that month."""
    if not value:
        return None
    year, month = (int(part) for part in value.split("-"))
    return date(year, month, 1)


def month_end(value: Optional[str]) -> Optional[date]:
    """Parses a "YYYY-MM" string into the last day of that month."""
    if not value:
        return None
    year, month = (int(part) for part in value.split("-"))
    return date(year, month, monthrange(year, month)[1])

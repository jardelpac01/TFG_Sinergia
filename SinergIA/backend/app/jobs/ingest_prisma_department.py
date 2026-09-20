"""Synchronize a Prisma department with OpenAlex.

Usage:
    python -m app.jobs.ingest_prisma_department I0A3
"""

import argparse
import sys
from collections import Counter
from datetime import datetime, timezone

from sqlmodel import Session

from app.database import engine
from app.jobs.backfill_institution_geo import backfill_institution_geo
from app.services.openalex_data import OpenAlexService, OpenAlexUpstreamError

DEFAULT_DEPARTMENT_CODE = "I0A3"


def ingest_prisma_department(department_code: str) -> int:
    started_at = datetime.now(timezone.utc)
    print(f"Starting Prisma/OpenAlex synchronization for department '{department_code}'...")

    try:
        with Session(engine) as db:
            results = OpenAlexService(db).ingest_authors_by_prisma_department(department_code)
    except OpenAlexUpstreamError as exc:
        print(f"Synchronization failed: {exc}", file=sys.stderr)
        return 1

    counts = Counter(item["status"] for item in results)
    elapsed_seconds = (datetime.now(timezone.utc) - started_at).total_seconds()

    print("Synchronization finished.")
    print(f"Department: {department_code}")
    print(f"Requested: {len(results)}")
    print(f"Created: {counts['created']}")
    print(f"Updated: {counts['updated']}")
    print(f"Skipped: {counts['skipped']}")
    print(f"Failed: {counts['failed']}")
    print(f"Duration: {elapsed_seconds:.1f}s")

    if counts["failed"]:
        print("Failed items:")
        for item in results:
            if item["status"] == "failed":
                print(
                    f"  [{item['prisma_id']}] "
                    f"{item.get('display_name') or 'Unknown'}: {item.get('error')}"
                )

    print("Backfilling missing institution coordinates...")
    geo_result = backfill_institution_geo()
    print(
        "Institution geo summary: "
        f"updated={geo_result.updated}, failed={geo_result.failed}, total={geo_result.total}"
    )

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Synchronize researchers from a Prisma department into OpenAlex data."
    )
    parser.add_argument(
        "department_code",
        nargs="?",
        default=DEFAULT_DEPARTMENT_CODE,
        help=f"Prisma department code to synchronize (default: {DEFAULT_DEPARTMENT_CODE}).",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return ingest_prisma_department(args.department_code)


if __name__ == "__main__":
    raise SystemExit(main())

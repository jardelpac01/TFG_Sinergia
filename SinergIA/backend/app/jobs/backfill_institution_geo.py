"""Backfill geo coordinates for institutions already stored in the database.

Usage:
    python -m app.jobs.backfill_institution_geo
"""

import argparse
import sys
import time
from dataclasses import dataclass

from sqlmodel import Session, select

from app.database import engine
from app.models import Institution
from app.services.http_client import fetch_with_retries


@dataclass
class InstitutionGeoBackfillResult:
    total: int
    updated: int
    failed: int


def backfill_institution_geo(batch_size: int = 25, sleep_seconds: float = 0.2) -> InstitutionGeoBackfillResult:
    with Session(engine) as db:
        institutions = db.exec(
            select(Institution).where(
                (Institution.geo_lat.is_(None)) | (Institution.geo_lon.is_(None))
            )
        ).all()

        total = len(institutions)
        print(f"Found {total} institutions without complete geo data.")

        updated = 0
        failed = 0
        for index, institution in enumerate(institutions, start=1):
            response = fetch_with_retries(
                f"https://api.openalex.org/institutions/{institution.id}",
                on_error=RuntimeError,
            )

            if response.status_code != 200:
                failed += 1
                print(
                    f"  [{institution.id}] failed: OpenAlex returned {response.status_code}",
                    file=sys.stderr,
                )
                continue

            data = response.json()
            geo = data.get("geo") or {}
            lat = geo.get("latitude")
            lon = geo.get("longitude")

            if lat is None or lon is None:
                failed += 1
                print(
                    f"  [{institution.id}] failed: OpenAlex has no coordinates.",
                    file=sys.stderr,
                )
                continue

            institution.geo_lat = lat
            institution.geo_lon = lon
            institution.city = geo.get("city")
            institution.homepage_url = data.get("homepage_url")
            institution.aliases = data.get("display_name_alternatives")
            institution.raw_data = data
            db.add(institution)
            updated += 1

            if index % batch_size == 0:
                db.commit()
                print(f"  progress: {index}/{total} (updated={updated}, failed={failed})")
                time.sleep(sleep_seconds)

        db.commit()

    print(f"Institution geo backfill finished. Updated {updated}, failed {failed}, out of {total}.")
    return InstitutionGeoBackfillResult(total=total, updated=updated, failed=failed)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch missing institution coordinates from OpenAlex."
    )
    parser.add_argument("--batch-size", type=int, default=25)
    parser.add_argument("--sleep-seconds", type=float, default=0.2)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    backfill_institution_geo(
        batch_size=args.batch_size,
        sleep_seconds=args.sleep_seconds,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

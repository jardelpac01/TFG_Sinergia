"""prevent duplicate author orcids

Revision ID: 7d5a8d74f0d2
Revises: d6ac8f4b9c21
Create Date: 2026-08-25 14:39:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7d5a8d74f0d2"
down_revision: Union[str, Sequence[str], None] = "d6ac8f4b9c21"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    rows = bind.execute(
        sa.text(
            """
            WITH ranked_authors AS (
                SELECT id, orcid,
                       ROW_NUMBER() OVER (
                           PARTITION BY orcid
                           ORDER BY updated_at DESC NULLS LAST, id
                       ) AS rn
                FROM authors
                WHERE orcid IS NOT NULL
            )
            SELECT id, orcid FROM ranked_authors WHERE rn > 1
            """
        )
    ).fetchall()

    for duplicate_id, orcid in rows:
        canonical_id = bind.execute(
            sa.text(
                """
                SELECT id
                FROM authors
                WHERE orcid = :orcid
                ORDER BY updated_at DESC NULLS LAST, id
                LIMIT 1
                """
            ),
            {"orcid": orcid},
        ).scalar()

        if canonical_id is None or canonical_id == duplicate_id:
            continue

        bind.execute(
            sa.text(
                """
                UPDATE author_topics SET author_id = :canonical_id WHERE author_id = :duplicate_id
                """
            ),
            {"canonical_id": canonical_id, "duplicate_id": duplicate_id},
        )
        bind.execute(
            sa.text(
                """
                UPDATE author_works SET author_id = :canonical_id WHERE author_id = :duplicate_id
                """
            ),
            {"canonical_id": canonical_id, "duplicate_id": duplicate_id},
        )
        bind.execute(
            sa.text(
                """
                UPDATE author_work_affiliations SET author_id = :canonical_id WHERE author_id = :duplicate_id
                """
            ),
            {"canonical_id": canonical_id, "duplicate_id": duplicate_id},
        )
        bind.execute(
            sa.text(
                """
                UPDATE users SET author_id = :canonical_id WHERE author_id = :duplicate_id
                """
            ),
            {"canonical_id": canonical_id, "duplicate_id": duplicate_id},
        )
        bind.execute(
            sa.text("DELETE FROM authors WHERE id = :duplicate_id AND id != :canonical_id"),
            {"duplicate_id": duplicate_id, "canonical_id": canonical_id},
        )

    op.execute(
        sa.text(
            "CREATE UNIQUE INDEX ix_authors_orcid_unique ON authors (orcid) WHERE orcid IS NOT NULL"
        )
    )


def downgrade() -> None:
    op.execute(sa.text("DROP INDEX IF EXISTS ix_authors_orcid_unique"))

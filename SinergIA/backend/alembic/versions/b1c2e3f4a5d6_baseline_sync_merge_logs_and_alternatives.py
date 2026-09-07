"""baseline sync, author merge logs, and display_name_alternatives

Revision ID: b1c2e3f4a5d6
Revises: fbba9437372f
Create Date: 2026-09-04 18:45:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "b1c2e3f4a5d6"
down_revision: Union[str, Sequence[str], None] = "fbba9437372f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = set(inspector.get_table_names())

    # --- baseline_sync_out_of_band_tables ---
    if "work_references" not in existing_tables:
        op.create_table(
            "work_references",
            sa.Column("work_id", sa.String(), nullable=False),
            sa.Column("referenced_work_id", sa.String(), nullable=False),
            sa.ForeignKeyConstraint(["work_id"], ["works.id"]),
            sa.ForeignKeyConstraint(["referenced_work_id"], ["works.id"]),
            sa.PrimaryKeyConstraint("work_id", "referenced_work_id"),
        )

    if "author_yearly_metrics" not in existing_tables:
        op.create_table(
            "author_yearly_metrics",
            sa.Column("author_id", sa.String(), nullable=False),
            sa.Column("year", sa.Integer(), nullable=False),
            sa.Column("works_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("cited_by_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("oa_works_count", sa.Integer(), nullable=False, server_default="0"),
            sa.ForeignKeyConstraint(["author_id"], ["authors.id"]),
            sa.PrimaryKeyConstraint("author_id", "year"),
        )

    # Deprecated by OpenAlex in favor of "topics"; drop if they exist.
    for table_name in ("work_concepts", "author_concepts", "concepts"):
        if table_name in existing_tables:
            op.drop_table(table_name)

    # `raw_affiliation` was added to the model but never migrated; it was
    # only present in the real DB via `create_all()`.
    existing_columns = {
        col["name"] for col in inspector.get_columns("author_work_affiliations")
    }
    if "raw_affiliation" not in existing_columns:
        op.add_column(
            "author_work_affiliations",
            sa.Column("raw_affiliation", sa.String(), nullable=True),
        )

    # --- add_author_merge_logs ---
    op.create_table(
        "author_merge_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("incoming_author_id", sa.String(length=255), nullable=False),
        sa.Column("incoming_display_name", sa.String(), nullable=False),
        sa.Column("matched_author_id", sa.String(length=255), nullable=False),
        sa.Column("matched_display_name", sa.String(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("score_breakdown", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["matched_author_id"], ["authors.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_author_merge_logs_incoming_author_id",
        "author_merge_logs",
        ["incoming_author_id"],
    )

    # --- add_authors_display_name_alternatives ---
    op.add_column(
        "authors",
        sa.Column(
            "display_name_alternatives",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("authors", "display_name_alternatives")

    op.drop_index("ix_author_merge_logs_incoming_author_id", table_name="author_merge_logs")
    op.drop_table("author_merge_logs")

    op.drop_column("author_work_affiliations", "raw_affiliation")
    op.create_table(
        "concepts",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("display_name", sa.String(), nullable=False),
        sa.Column("level", sa.Integer(), nullable=True),
        sa.Column("wikidata", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("raw_data", postgresql.JSONB(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "author_concepts",
        sa.Column("author_id", sa.String(), nullable=False),
        sa.Column("concept_id", sa.String(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False, server_default="0.0"),
        sa.ForeignKeyConstraint(["author_id"], ["authors.id"]),
        sa.ForeignKeyConstraint(["concept_id"], ["concepts.id"]),
        sa.PrimaryKeyConstraint("author_id", "concept_id"),
    )
    op.create_table(
        "work_concepts",
        sa.Column("work_id", sa.String(), nullable=False),
        sa.Column("concept_id", sa.String(), nullable=False),
        sa.Column("score", sa.Float(), nullable=False, server_default="0.0"),
        sa.ForeignKeyConstraint(["work_id"], ["works.id"]),
        sa.ForeignKeyConstraint(["concept_id"], ["concepts.id"]),
        sa.PrimaryKeyConstraint("work_id", "concept_id"),
    )

    op.drop_table("author_yearly_metrics")
    op.drop_table("work_references")

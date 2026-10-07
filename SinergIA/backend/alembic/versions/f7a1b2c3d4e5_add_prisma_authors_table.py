"""add prisma_authors table

Revision ID: f7a1b2c3d4e5
Revises: b1c2e3f4a5d6
Create Date: 2026-09-04
"""
from alembic import op
import sqlalchemy as sa


revision = "f7a1b2c3d4e5"
down_revision = "b1c2e3f4a5d6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "prisma_authors",
        sa.Column("prisma_id", sa.Integer(), nullable=False),
        sa.Column("display_name", sa.String(), nullable=False),
        sa.Column("department", sa.String(length=255), nullable=True),
        sa.Column("orcid", sa.String(length=255), nullable=True),
        sa.Column("openalex_author_id", sa.String(length=255), nullable=True),
        sa.Column("dialnet_code", sa.String(length=255), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("prisma_id"),
    )
    op.create_index(
        "ix_prisma_authors_openalex_author_id",
        "prisma_authors",
        ["openalex_author_id"],
    )
    op.create_unique_constraint(
        "uq_prisma_authors_orcid", "prisma_authors", ["orcid"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_prisma_authors_orcid", "prisma_authors", type_="unique")
    op.drop_index("ix_prisma_authors_openalex_author_id", table_name="prisma_authors")
    op.drop_table("prisma_authors")

"""sync Prisma research groups

Revision ID: c4e8f1a2b3d5
Revises: a3c9d1e7b2f4
Create Date: 2026-09-19
"""

from alembic import op
import sqlalchemy as sa


revision = "c4e8f1a2b3d5"
down_revision = "a3c9d1e7b2f4"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "research_groups",
        sa.Column("code", sa.String(length=50), nullable=True),
    )
    op.create_index(
        "ix_research_groups_code",
        "research_groups",
        ["code"],
        unique=True,
    )
    op.add_column(
        "prisma_authors",
        sa.Column("research_group_code", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "prisma_authors",
        sa.Column("research_group_name", sa.String(length=255), nullable=True),
    )
    op.create_index(
        "ix_prisma_authors_research_group_code",
        "prisma_authors",
        ["research_group_code"],
    )

    connection = op.get_bind()
    connection.execute(
        sa.text(
            """
            UPDATE authors
            SET research_group_id = NULL
            WHERE research_group_id IN (
                SELECT id
                FROM research_groups
                WHERE lower(name) IN (
                    'minerva',
                    'minerva - artificial intelligence research lab'
                )
            )
            """
        )
    )
    connection.execute(
        sa.text(
            """
            DELETE FROM research_groups
            WHERE lower(name) IN (
                'minerva',
                'minerva - artificial intelligence research lab'
            )
            """
        )
    )


def downgrade() -> None:
    op.drop_index(
        "ix_prisma_authors_research_group_code",
        table_name="prisma_authors",
    )
    op.drop_column("prisma_authors", "research_group_name")
    op.drop_column("prisma_authors", "research_group_code")
    op.drop_index("ix_research_groups_code", table_name="research_groups")
    op.drop_column("research_groups", "code")

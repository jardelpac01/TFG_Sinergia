"""enable unaccent extension

Revision ID: a3c9d1e7b2f4
Revises: f7a1b2c3d4e5
Create Date: 2026-09-15
"""
from alembic import op


revision = "a3c9d1e7b2f4"
down_revision = "f7a1b2c3d4e5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS unaccent;")


def downgrade() -> None:
    op.execute("DROP EXTENSION IF EXISTS unaccent;")

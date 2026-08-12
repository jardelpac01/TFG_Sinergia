"""add_string_length_limits_for_user_fields

Revision ID: d6ac8f4b9c21
Revises: d16942e267fa
Create Date: 2026-08-12 18:06:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d6ac8f4b9c21"
down_revision: Union[str, Sequence[str], None] = "d16942e267fa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "username",
        existing_type=sa.VARCHAR(),
        type_=sa.String(length=150),
        existing_nullable=False,
        postgresql_using="username::varchar(150)",
    )
    op.alter_column(
        "users",
        "email",
        existing_type=sa.VARCHAR(),
        type_=sa.String(length=254),
        existing_nullable=False,
        postgresql_using="email::varchar(254)",
    )
    op.alter_column(
        "users",
        "password_hash",
        existing_type=sa.VARCHAR(),
        type_=sa.String(length=255),
        existing_nullable=False,
        postgresql_using="password_hash::varchar(255)",
    )
    op.alter_column(
        "users",
        "role",
        existing_type=sa.VARCHAR(),
        type_=sa.String(length=20),
        existing_nullable=False,
        postgresql_using="role::varchar(20)",
    )
    op.alter_column(
        "users",
        "author_id",
        existing_type=sa.VARCHAR(),
        type_=sa.String(length=255),
        existing_nullable=True,
        postgresql_using="author_id::varchar(255)",
    )

    op.alter_column(
        "user_logs",
        "action",
        existing_type=sa.VARCHAR(),
        type_=sa.String(length=100),
        existing_nullable=False,
        postgresql_using="action::varchar(100)",
    )
    op.alter_column(
        "user_logs",
        "target_entity",
        existing_type=sa.VARCHAR(),
        type_=sa.String(length=100),
        existing_nullable=True,
        postgresql_using="target_entity::varchar(100)",
    )
    op.alter_column(
        "user_logs",
        "ip_address",
        existing_type=sa.VARCHAR(),
        type_=sa.String(length=45),
        existing_nullable=True,
        postgresql_using="ip_address::varchar(45)",
    )


def downgrade() -> None:
    op.alter_column(
        "user_logs",
        "ip_address",
        existing_type=sa.String(length=45),
        type_=sa.VARCHAR(),
        existing_nullable=True,
        postgresql_using="ip_address::varchar",
    )
    op.alter_column(
        "user_logs",
        "target_entity",
        existing_type=sa.String(length=100),
        type_=sa.VARCHAR(),
        existing_nullable=True,
        postgresql_using="target_entity::varchar",
    )
    op.alter_column(
        "user_logs",
        "action",
        existing_type=sa.String(length=100),
        type_=sa.VARCHAR(),
        existing_nullable=False,
        postgresql_using="action::varchar",
    )

    op.alter_column(
        "users",
        "author_id",
        existing_type=sa.String(length=255),
        type_=sa.VARCHAR(),
        existing_nullable=True,
        postgresql_using="author_id::varchar",
    )
    op.alter_column(
        "users",
        "role",
        existing_type=sa.String(length=20),
        type_=sa.VARCHAR(),
        existing_nullable=False,
        postgresql_using="role::varchar",
    )
    op.alter_column(
        "users",
        "password_hash",
        existing_type=sa.String(length=255),
        type_=sa.VARCHAR(),
        existing_nullable=False,
        postgresql_using="password_hash::varchar",
    )
    op.alter_column(
        "users",
        "email",
        existing_type=sa.String(length=254),
        type_=sa.VARCHAR(),
        existing_nullable=False,
        postgresql_using="email::varchar",
    )
    op.alter_column(
        "users",
        "username",
        existing_type=sa.String(length=150),
        type_=sa.VARCHAR(),
        existing_nullable=False,
        postgresql_using="username::varchar",
    )

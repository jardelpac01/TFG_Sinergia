"""add research_groups table and authors.research_group_id

Revision ID: fbba9437372f
Revises: 7d5a8d74f0d2
Create Date: 2026-09-02 12:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "fbba9437372f"
down_revision: Union[str, Sequence[str], None] = "7d5a8d74f0d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

MINERVA_GROUP_NAME = "Minerva - Artificial Intelligence Research Lab"
MINERVA_GROUP_URL = "https://grupo.us.es/minerva/equipo/"

# Members listed on https://grupo.us.es/minerva/equipo/, matched to existing
# `authors.id` (OpenAlex author IDs) by name, since names are stored with
# OpenAlex's normalized formatting (accents/hyphenation may differ slightly
# from the group website). Members not found in the authors table are
# skipped and can be linked later once they are ingested.
MINERVA_AUTHOR_IDS = [
    "A5036001529",  # José C. Riquelme
    "A5056290040",  # Cristina Rubio-Escudero
    "A5018933874",  # Isabel A. Nepomuceno-Chamorro
    "A5028880020",  # M. Martínez-Ballesteros
    "A5044384169",  # Daniel Mateos-García
    "A5080735284",  # Beatriz Pontes
    "A5042668863",  # Juan A. Nepomuceno
    "A5087784610",  # José María Luna-Romera
    "A5032952434",  # David Gutiérrez-Avilés
    "A5077117115",  # Belén Vega-Márquez
    "A5059940512",  # Manuel Carranza-García
    "A5006954487",  # M. J. Jiménez-Navarro
    "A5092921902",  # Jose E. Sánchez-López
    "A5024287902",  # F. Javier Galán-Sales
    "A5099092679",  # Ana Rodríguez-López
    # Pablo Reina Jiménez: not currently present in the authors table.
]


def upgrade() -> None:
    bind = op.get_bind()

    op.create_table(
        "research_groups",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("website_url", sa.String(), nullable=True),
        sa.UniqueConstraint("name", name="uq_research_groups_name"),
    )
    op.create_index("ix_research_groups_name", "research_groups", ["name"])

    op.add_column(
        "authors",
        sa.Column("research_group_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_authors_research_group_id",
        "authors",
        "research_groups",
        ["research_group_id"],
        ["id"],
    )

    minerva_group_id = bind.execute(
        sa.text(
            "INSERT INTO research_groups (name, description, website_url) VALUES (:name, :description, :url) RETURNING id"
        ),
        {
            "name": MINERVA_GROUP_NAME,
            "description": "Grupo de investigación Minerva (Universidad de Sevilla).",
            "url": MINERVA_GROUP_URL,
        },
    ).scalar()


    bind.execute(
        sa.text(
            "UPDATE authors SET research_group_id = :group_id WHERE id = ANY(:ids)"
        ),
        {"group_id": minerva_group_id, "ids": MINERVA_AUTHOR_IDS},
    )


def downgrade() -> None:
    op.drop_constraint("fk_authors_research_group_id", "authors", type_="foreignkey")
    op.drop_column("authors", "research_group_id")
    op.drop_index("ix_research_groups_name", table_name="research_groups")
    op.drop_table("research_groups")

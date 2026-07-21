"""create projects table

Revision ID: 0002_create_projects
Revises: 0001_create_vaults
Create Date: 2026-07-21
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0002_create_projects"
down_revision = "0001_create_vaults"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("vault_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.CheckConstraint(
            "char_length(name) >= 3 AND char_length(name) <= 100",
            name="ck_projects_name_length",
        ),
        sa.CheckConstraint("name = btrim(name)", name="ck_projects_name_trimmed"),
        sa.ForeignKeyConstraint(
            ["vault_id"],
            ["vaults.id"],
            name="fk_projects_vault_id_vaults",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_projects"),
        sa.UniqueConstraint("vault_id", "name", name="uq_projects_vault_id_name"),
    )
    op.create_index("ix_projects_vault_id", "projects", ["vault_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_projects_vault_id", table_name="projects")
    op.drop_table("projects")

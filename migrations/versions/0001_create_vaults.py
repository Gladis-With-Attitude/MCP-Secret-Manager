"""create vaults table

Revision ID: 0001_create_vaults
Revises:
Create Date: 2026-07-21
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001_create_vaults"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "vaults",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.CheckConstraint(
            "char_length(name) >= 3 AND char_length(name) <= 100",
            name="ck_vaults_name_length",
        ),
        sa.CheckConstraint("name = btrim(name)", name="ck_vaults_name_trimmed"),
        sa.PrimaryKeyConstraint("id", name="pk_vaults"),
        sa.UniqueConstraint("name", name="uq_vaults_name"),
    )


def downgrade() -> None:
    op.drop_table("vaults")

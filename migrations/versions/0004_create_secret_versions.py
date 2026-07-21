"""create secret versions table

Revision ID: 0004_create_secret_versions
Revises: 0003_create_secrets
Create Date: 2026-07-21
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0004_create_secret_versions"
down_revision = "0003_create_secrets"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "secret_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("secret_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("version >= 1", name="ck_secret_versions_version_positive"),
        sa.CheckConstraint(
            "char_length(value) >= 1",
            name="ck_secret_versions_value_required",
        ),
        sa.ForeignKeyConstraint(
            ["secret_id"],
            ["secrets.id"],
            name="fk_secret_versions_secret_id_secrets",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_secret_versions"),
    )
    op.create_index(
        "ix_secret_versions_secret_id",
        "secret_versions",
        ["secret_id"],
        unique=False,
    )
    op.create_index(
        "uq_secret_versions_secret_id_version",
        "secret_versions",
        ["secret_id", "version"],
        unique=True,
    )
    op.create_index(
        "uq_secret_versions_active_secret_id",
        "secret_versions",
        ["secret_id"],
        unique=True,
        postgresql_where=sa.text("active = true"),
    )


def downgrade() -> None:
    op.drop_index("uq_secret_versions_active_secret_id", table_name="secret_versions")
    op.drop_index("uq_secret_versions_secret_id_version", table_name="secret_versions")
    op.drop_index("ix_secret_versions_secret_id", table_name="secret_versions")
    op.drop_table("secret_versions")

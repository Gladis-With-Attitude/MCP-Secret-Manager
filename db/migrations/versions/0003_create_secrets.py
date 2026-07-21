"""create secrets table

Revision ID: 0003_create_secrets
Revises: 0002_create_projects
Create Date: 2026-07-21
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0003_create_secrets"
down_revision = "0002_create_projects"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "secrets",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.CheckConstraint(
            "char_length(key) >= 3 AND char_length(key) <= 128",
            name="ck_secrets_key_length",
        ),
        sa.CheckConstraint("key ~ '^[A-Z0-9_]+$'", name="ck_secrets_key_format"),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name="fk_secrets_project_id_projects",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_secrets"),
        sa.UniqueConstraint("project_id", "key", name="uq_secrets_project_id_key"),
    )
    op.create_index("ix_secrets_project_id", "secrets", ["project_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_secrets_project_id", table_name="secrets")
    op.drop_table("secrets")

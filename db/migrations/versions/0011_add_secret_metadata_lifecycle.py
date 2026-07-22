"""add secret metadata lifecycle

Revision ID: 0011_secret_lifecycle
Revises: 0010_add_project_lifecycle
Create Date: 2026-07-22
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0011_secret_lifecycle"
down_revision = "0010_add_project_lifecycle"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "secrets",
        sa.Column("type", sa.String(length=40), server_default="generic", nullable=False),
    )
    op.add_column(
        "secrets",
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
    )
    op.add_column(
        "secrets",
        sa.Column(
            "tags",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
    )
    op.add_column(
        "secrets",
        sa.Column("archived", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    op.add_column(
        "secrets",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.add_column(
        "secrets",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.add_column("secrets", sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_secrets_archived", "secrets", ["archived"])
    op.create_index("ix_secrets_type", "secrets", ["type"])


def downgrade() -> None:
    op.drop_index("ix_secrets_type", table_name="secrets")
    op.drop_index("ix_secrets_archived", table_name="secrets")
    op.drop_column("secrets", "archived_at")
    op.drop_column("secrets", "updated_at")
    op.drop_column("secrets", "created_at")
    op.drop_column("secrets", "archived")
    op.drop_column("secrets", "tags")
    op.drop_column("secrets", "metadata")
    op.drop_column("secrets", "type")

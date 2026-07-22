"""add vault lifecycle metadata

Revision ID: 0009_add_vault_lifecycle
Revises: 0008_create_audit_events
Create Date: 2026-07-22
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0009_add_vault_lifecycle"
down_revision = "0008_create_audit_events"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("vaults", sa.Column("description", sa.Text(), nullable=True))
    op.add_column(
        "vaults",
        sa.Column("archived", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    op.add_column(
        "vaults",
        sa.Column("locked", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    op.add_column(
        "vaults",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.add_column(
        "vaults",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.add_column("vaults", sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_vaults_archived", "vaults", ["archived"])
    op.create_index("ix_vaults_locked", "vaults", ["locked"])


def downgrade() -> None:
    op.drop_index("ix_vaults_locked", table_name="vaults")
    op.drop_index("ix_vaults_archived", table_name="vaults")
    op.drop_column("vaults", "archived_at")
    op.drop_column("vaults", "updated_at")
    op.drop_column("vaults", "created_at")
    op.drop_column("vaults", "locked")
    op.drop_column("vaults", "archived")
    op.drop_column("vaults", "description")

"""add project lifecycle metadata

Revision ID: 0010_add_project_lifecycle
Revises: 0009_add_vault_lifecycle
Create Date: 2026-07-22
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0010_add_project_lifecycle"
down_revision = "0009_add_vault_lifecycle"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("projects", sa.Column("description", sa.Text(), nullable=True))
    op.add_column(
        "projects",
        sa.Column("archived", sa.Boolean(), server_default=sa.false(), nullable=False),
    )
    op.add_column(
        "projects",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.add_column(
        "projects",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.add_column("projects", sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("ix_projects_archived", "projects", ["archived"])


def downgrade() -> None:
    op.drop_index("ix_projects_archived", table_name="projects")
    op.drop_column("projects", "archived_at")
    op.drop_column("projects", "updated_at")
    op.drop_column("projects", "created_at")
    op.drop_column("projects", "archived")
    op.drop_column("projects", "description")

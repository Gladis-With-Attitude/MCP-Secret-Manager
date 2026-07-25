"""create user preferences

Revision ID: 0014_create_user_preferences
Revises: 0013_add_api_key_metadata
Create Date: 2026-07-24
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0014_create_user_preferences"
down_revision = "0013_add_api_key_metadata"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "user_preferences",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("organization", sa.String(length=120), nullable=True),
        sa.Column("avatar_url", sa.String(length=2048), nullable=True),
        sa.Column("theme", sa.String(length=32), nullable=False),
        sa.Column("language", sa.String(length=16), nullable=False),
        sa.Column("timezone", sa.String(length=80), nullable=False),
        sa.Column("date_time_format", sa.String(length=32), nullable=False),
        sa.Column("display_density", sa.String(length=32), nullable=False),
        sa.Column("audit_alerts", sa.Boolean(), nullable=False),
        sa.Column("email_enabled", sa.Boolean(), nullable=False),
        sa.Column("in_app_enabled", sa.Boolean(), nullable=False),
        sa.Column("product_updates", sa.Boolean(), nullable=False),
        sa.Column("security_alerts", sa.Boolean(), nullable=False),
        sa.CheckConstraint(
            "theme IN ('light', 'dark', 'system')",
            name="ck_user_preferences_theme_valid",
        ),
        sa.CheckConstraint(
            "language IN ('en', 'fr')",
            name="ck_user_preferences_language_valid",
        ),
        sa.CheckConstraint(
            "date_time_format IN ('absolute', 'relative', 'short')",
            name="ck_user_preferences_date_time_format_valid",
        ),
        sa.CheckConstraint(
            "display_density IN ('comfortable', 'compact')",
            name="ck_user_preferences_display_density_valid",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_user_preferences_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("user_id"),
    )


def downgrade() -> None:
    op.drop_table("user_preferences")

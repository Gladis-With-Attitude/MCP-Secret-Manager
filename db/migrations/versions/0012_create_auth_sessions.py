"""create auth sessions

Revision ID: 0012_auth_sessions
Revises: 0011_secret_lifecycle
Create Date: 2026-07-23
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0012_auth_sessions"
down_revision = "0011_secret_lifecycle"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "auth_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("hashed_token", sa.Text(), nullable=False),
        sa.Column("token_prefix", sa.String(length=64), nullable=False),
        sa.Column("api_key_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("owner_type", sa.String(length=32), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "char_length(hashed_token) >= 1",
            name="ck_auth_sessions_hash_required",
        ),
        sa.CheckConstraint(
            "char_length(token_prefix) >= 1",
            name="ck_auth_sessions_prefix_required",
        ),
        sa.CheckConstraint(
            "owner_type IN ('user', 'service_account')",
            name="ck_auth_sessions_owner_type_valid",
        ),
        sa.ForeignKeyConstraint(
            ["api_key_id"],
            ["api_keys.id"],
            name="fk_auth_sessions_api_key_id_api_keys",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "uq_auth_sessions_token_prefix",
        "auth_sessions",
        ["token_prefix"],
        unique=True,
    )
    op.create_index("ix_auth_sessions_api_key_id", "auth_sessions", ["api_key_id"])
    op.create_index("ix_auth_sessions_owner", "auth_sessions", ["owner_type", "owner_id"])


def downgrade() -> None:
    op.drop_index("ix_auth_sessions_owner", table_name="auth_sessions")
    op.drop_index("ix_auth_sessions_api_key_id", table_name="auth_sessions")
    op.drop_index("uq_auth_sessions_token_prefix", table_name="auth_sessions")
    op.drop_table("auth_sessions")

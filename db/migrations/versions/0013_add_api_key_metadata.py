"""add api key metadata

Revision ID: 0013_add_api_key_metadata
Revises: 0012_create_auth_sessions
Create Date: 2026-07-23
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "0013_add_api_key_metadata"
down_revision = "0012_create_auth_sessions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("api_keys", sa.Column("name", sa.String(length=120), nullable=True))
    op.add_column("api_keys", sa.Column("description", sa.Text(), nullable=True))
    op.add_column(
        "api_keys",
        sa.Column(
            "granted_permissions",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'::json"),
        ),
    )
    op.add_column(
        "api_keys",
        sa.Column("scopes", sa.JSON(), nullable=False, server_default=sa.text("'[]'::json")),
    )
    op.create_check_constraint(
        "ck_api_keys_name_valid",
        "api_keys",
        "name IS NULL OR char_length(name) >= 1",
    )
    op.create_index("ix_api_keys_status", "api_keys", ["revoked_at", "expires_at"], unique=False)
    op.alter_column("api_keys", "granted_permissions", server_default=None)
    op.alter_column("api_keys", "scopes", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_api_keys_status", table_name="api_keys")
    op.drop_constraint("ck_api_keys_name_valid", "api_keys", type_="check")
    op.drop_column("api_keys", "scopes")
    op.drop_column("api_keys", "granted_permissions")
    op.drop_column("api_keys", "description")
    op.drop_column("api_keys", "name")

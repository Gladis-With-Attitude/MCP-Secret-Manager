"""create identity tables

Revision ID: 0006_create_identity_tables
Revises: 0005_encrypt_secret_versions
Create Date: 2026-07-21
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0006_create_identity_tables"
down_revision = "0005_encrypt_secret_versions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("char_length(email) >= 3", name="ck_users_email_required"),
        sa.CheckConstraint(
            "char_length(display_name) >= 1",
            name="ck_users_display_name_required",
        ),
        sa.CheckConstraint("status IN ('active', 'disabled')", name="ck_users_status_valid"),
        sa.PrimaryKeyConstraint("id", name="pk_users"),
    )
    op.create_index("uq_users_email", "users", ["email"], unique=True)

    op.create_table(
        "service_accounts",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "char_length(name) >= 3",
            name="ck_service_accounts_name_min_length",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'disabled')",
            name="ck_service_accounts_status_valid",
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name="fk_service_accounts_project_id_projects",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_service_accounts"),
    )
    op.create_index(
        "ix_service_accounts_project_id",
        "service_accounts",
        ["project_id"],
        unique=False,
    )
    op.create_index(
        "uq_service_accounts_project_id_name",
        "service_accounts",
        ["project_id", "name"],
        unique=True,
    )

    op.create_table(
        "api_keys",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("hashed_key", sa.Text(), nullable=False),
        sa.Column("key_prefix", sa.String(length=32), nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("owner_type", sa.String(length=32), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "char_length(hashed_key) >= 1",
            name="ck_api_keys_hashed_key_required",
        ),
        sa.CheckConstraint(
            "char_length(key_prefix) >= 1",
            name="ck_api_keys_key_prefix_required",
        ),
        sa.CheckConstraint(
            "owner_type IN ('user', 'service_account')",
            name="ck_api_keys_owner_type_valid",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_api_keys"),
    )
    op.create_index("uq_api_keys_key_prefix", "api_keys", ["key_prefix"], unique=True)
    op.create_index("ix_api_keys_owner", "api_keys", ["owner_type", "owner_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_api_keys_owner", table_name="api_keys")
    op.drop_index("uq_api_keys_key_prefix", table_name="api_keys")
    op.drop_table("api_keys")
    op.drop_index("uq_service_accounts_project_id_name", table_name="service_accounts")
    op.drop_index("ix_service_accounts_project_id", table_name="service_accounts")
    op.drop_table("service_accounts")
    op.drop_index("uq_users_email", table_name="users")
    op.drop_table("users")

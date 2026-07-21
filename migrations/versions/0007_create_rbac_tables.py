"""create rbac tables

Revision ID: 0007_create_rbac_tables
Revises: 0006_create_identity_tables
Create Date: 2026-07-21
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0007_create_rbac_tables"
down_revision = "0006_create_identity_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "permissions",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.CheckConstraint("char_length(name) >= 1", name="ck_permissions_name_required"),
        sa.PrimaryKeyConstraint("id", name="pk_permissions"),
    )
    op.create_index("uq_permissions_name", "permissions", ["name"], unique=True)

    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.CheckConstraint("char_length(name) >= 1", name="ck_roles_name_required"),
        sa.PrimaryKeyConstraint("id", name="pk_roles"),
    )
    op.create_index("uq_roles_name", "roles", ["name"], unique=True)

    op.create_table(
        "role_permissions",
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("permission_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
            name="fk_role_permissions_role_id_roles",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["permission_id"],
            ["permissions.id"],
            name="fk_role_permissions_permission_id_permissions",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("role_id", "permission_id", name="pk_role_permissions"),
    )
    op.create_index(
        "uq_role_permissions_role_id_permission_id",
        "role_permissions",
        ["role_id", "permission_id"],
        unique=True,
    )
    op.create_index(
        "ix_role_permissions_permission_id",
        "role_permissions",
        ["permission_id"],
        unique=False,
    )

    op.create_table(
        "role_assignments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("identity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("identity_type", sa.String(length=32), nullable=False),
        sa.Column("scope_type", sa.String(length=32), nullable=False),
        sa.Column("scope_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "identity_type IN ('user', 'service_account')",
            name="ck_role_assignments_identity_type_valid",
        ),
        sa.CheckConstraint(
            "scope_type IN ('global', 'vault', 'project', 'secret')",
            name="ck_role_assignments_scope_type_valid",
        ),
        sa.CheckConstraint(
            "(scope_type = 'global' AND scope_id IS NULL) OR "
            "(scope_type <> 'global' AND scope_id IS NOT NULL)",
            name="ck_role_assignments_scope_id_required",
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["roles.id"],
            name="fk_role_assignments_role_id_roles",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_role_assignments"),
    )
    op.create_index(
        "uq_role_assignments_identity_scope_role",
        "role_assignments",
        ["identity_type", "identity_id", "scope_type", "scope_id", "role_id"],
        unique=True,
    )
    op.create_index(
        "uq_role_assignments_global_identity_role",
        "role_assignments",
        ["identity_type", "identity_id", "role_id"],
        unique=True,
        postgresql_where=sa.text("scope_type = 'global'"),
    )
    op.create_index(
        "ix_role_assignments_identity",
        "role_assignments",
        ["identity_type", "identity_id"],
        unique=False,
    )
    op.create_index(
        "ix_role_assignments_scope",
        "role_assignments",
        ["scope_type", "scope_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_role_assignments_scope", table_name="role_assignments")
    op.drop_index("ix_role_assignments_identity", table_name="role_assignments")
    op.drop_index("uq_role_assignments_global_identity_role", table_name="role_assignments")
    op.drop_index("uq_role_assignments_identity_scope_role", table_name="role_assignments")
    op.drop_table("role_assignments")
    op.drop_index("ix_role_permissions_permission_id", table_name="role_permissions")
    op.drop_index("uq_role_permissions_role_id_permission_id", table_name="role_permissions")
    op.drop_table("role_permissions")
    op.drop_index("uq_roles_name", table_name="roles")
    op.drop_table("roles")
    op.drop_index("uq_permissions_name", table_name="permissions")
    op.drop_table("permissions")

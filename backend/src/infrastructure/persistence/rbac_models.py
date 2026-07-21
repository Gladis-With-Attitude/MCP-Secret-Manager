from __future__ import annotations

from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from domain.identity.value_objects import ApiKeyOwnerType, ServiceAccountId, UserId
from domain.rbac.entities import Permission, Role, RoleAssignment
from domain.rbac.value_objects import (
    PermissionId,
    PermissionName,
    RoleAssignmentId,
    RoleId,
    RoleName,
    ScopeType,
)
from infrastructure.persistence.base import Base


class PermissionModel(Base):
    __tablename__ = "permissions"
    __table_args__ = (
        CheckConstraint("char_length(name) >= 1", name="ck_permissions_name_required"),
        Index("uq_permissions_name", "name", unique=True),
    )

    id: Mapped[UUID] = mapped_column(postgresql.UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(length=120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    @classmethod
    def from_domain(cls, permission: Permission) -> PermissionModel:
        return cls(
            id=permission.id.value,
            name=permission.name.value,
            description=permission.description,
        )

    def to_domain(self) -> Permission:
        return Permission(
            id=PermissionId(self.id),
            name=PermissionName(self.name),
            description=self.description,
        )


class RoleModel(Base):
    __tablename__ = "roles"
    __table_args__ = (
        CheckConstraint("char_length(name) >= 1", name="ck_roles_name_required"),
        Index("uq_roles_name", "name", unique=True),
    )

    id: Mapped[UUID] = mapped_column(postgresql.UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(length=100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    @classmethod
    def from_domain(cls, role: Role) -> RoleModel:
        return cls(id=role.id.value, name=role.name.value, description=role.description)

    def to_domain(self) -> Role:
        return Role(id=RoleId(self.id), name=RoleName(self.name), description=self.description)


class RolePermissionModel(Base):
    __tablename__ = "role_permissions"
    __table_args__ = (
        Index("uq_role_permissions_role_id_permission_id", "role_id", "permission_id", unique=True),
        Index("ix_role_permissions_permission_id", "permission_id"),
    )

    role_id: Mapped[UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("roles.id", name="fk_role_permissions_role_id_roles", ondelete="CASCADE"),
        primary_key=True,
    )
    permission_id: Mapped[UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey(
            "permissions.id",
            name="fk_role_permissions_permission_id_permissions",
            ondelete="CASCADE",
        ),
        primary_key=True,
    )


class RoleAssignmentModel(Base):
    __tablename__ = "role_assignments"
    __table_args__ = (
        CheckConstraint(
            "identity_type IN ('user', 'service_account')",
            name="ck_role_assignments_identity_type_valid",
        ),
        CheckConstraint(
            "scope_type IN ('global', 'vault', 'project', 'secret')",
            name="ck_role_assignments_scope_type_valid",
        ),
        CheckConstraint(
            "(scope_type = 'global' AND scope_id IS NULL) OR "
            "(scope_type <> 'global' AND scope_id IS NOT NULL)",
            name="ck_role_assignments_scope_id_required",
        ),
        Index(
            "uq_role_assignments_identity_scope_role",
            "identity_type",
            "identity_id",
            "scope_type",
            "scope_id",
            "role_id",
            unique=True,
        ),
        Index(
            "uq_role_assignments_global_identity_role",
            "identity_type",
            "identity_id",
            "role_id",
            unique=True,
            postgresql_where=text("scope_type = 'global'"),
        ),
        Index("ix_role_assignments_identity", "identity_type", "identity_id"),
        Index("ix_role_assignments_scope", "scope_type", "scope_id"),
    )

    id: Mapped[UUID] = mapped_column(postgresql.UUID(as_uuid=True), primary_key=True)
    identity_id: Mapped[UUID] = mapped_column(postgresql.UUID(as_uuid=True), nullable=False)
    identity_type: Mapped[str] = mapped_column(String(length=32), nullable=False)
    scope_type: Mapped[str] = mapped_column(String(length=32), nullable=False)
    scope_id: Mapped[UUID | None] = mapped_column(postgresql.UUID(as_uuid=True), nullable=True)
    role_id: Mapped[UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("roles.id", name="fk_role_assignments_role_id_roles", ondelete="CASCADE"),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    @classmethod
    def from_domain(cls, role_assignment: RoleAssignment) -> RoleAssignmentModel:
        return cls(
            id=role_assignment.id.value,
            identity_id=role_assignment.identity_id.value,
            identity_type=role_assignment.identity_type.value,
            scope_type=role_assignment.scope_type.value,
            scope_id=role_assignment.scope_id,
            role_id=role_assignment.role_id.value,
            created_at=role_assignment.created_at,
        )

    def to_domain(self) -> RoleAssignment:
        identity_type = ApiKeyOwnerType(self.identity_type)
        identity_id: UserId | ServiceAccountId
        if identity_type is ApiKeyOwnerType.USER:
            identity_id = UserId(self.identity_id)
        else:
            identity_id = ServiceAccountId(self.identity_id)
        return RoleAssignment(
            id=RoleAssignmentId(self.id),
            identity_id=identity_id,
            identity_type=identity_type,
            scope_type=ScopeType(self.scope_type),
            scope_id=self.scope_id,
            role_id=RoleId(self.role_id),
            created_at=self.created_at,
        )

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID

from domain.identity.value_objects import ApiKeyOwnerType, ServiceAccountId, UserId
from domain.rbac.exceptions import RbacValueError
from domain.rbac.value_objects import (
    PermissionId,
    PermissionName,
    RoleAssignmentId,
    RoleId,
    RoleName,
    ScopeType,
)


@dataclass(frozen=True, slots=True, eq=False)
class Permission:
    id: PermissionId
    name: PermissionName
    description: str | None

    @classmethod
    def create(cls, name: PermissionName, description: str | None) -> Permission:
        return cls(id=PermissionId.new(), name=name, description=description)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Permission):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


@dataclass(frozen=True, slots=True, eq=False)
class Role:
    id: RoleId
    name: RoleName
    description: str | None

    @classmethod
    def create(cls, name: RoleName, description: str | None) -> Role:
        return cls(id=RoleId.new(), name=name, description=description)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Role):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


@dataclass(frozen=True, slots=True, eq=False)
class RoleAssignment:
    id: RoleAssignmentId
    identity_id: UserId | ServiceAccountId
    identity_type: ApiKeyOwnerType
    scope_type: ScopeType
    scope_id: UUID | None
    role_id: RoleId
    created_at: datetime

    @classmethod
    def create(
        cls,
        identity_id: UserId | ServiceAccountId,
        identity_type: ApiKeyOwnerType,
        scope_type: ScopeType,
        scope_id: UUID | None,
        role_id: RoleId,
    ) -> RoleAssignment:
        if scope_type is ScopeType.GLOBAL and scope_id is not None:
            msg = "Global role assignments cannot have a scope id."
            raise RbacValueError(msg)
        if scope_type is not ScopeType.GLOBAL and scope_id is None:
            msg = "Scoped role assignments require a scope id."
            raise RbacValueError(msg)
        return cls(
            id=RoleAssignmentId.new(),
            identity_id=identity_id,
            identity_type=identity_type,
            scope_type=scope_type,
            scope_id=scope_id,
            role_id=role_id,
            created_at=datetime.now(UTC),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RoleAssignment):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

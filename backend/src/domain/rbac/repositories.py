from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

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


class PermissionRepositoryConflictError(RuntimeError):
    """Raised when persistence detects a Permission constraint conflict."""


class RoleRepositoryConflictError(RuntimeError):
    """Raised when persistence detects a Role constraint conflict."""


class RoleAssignmentRepositoryConflictError(RuntimeError):
    """Raised when persistence detects a RoleAssignment constraint conflict."""


class PermissionRepository(Protocol):
    async def create(self, permission: Permission) -> Permission:
        raise NotImplementedError

    async def get(self, permission_id: PermissionId) -> Permission | None:
        raise NotImplementedError

    async def get_by_name(self, name: PermissionName) -> Permission | None:
        raise NotImplementedError

    async def list(self) -> Sequence[Permission]:
        raise NotImplementedError


class RoleRepository(Protocol):
    async def create(self, role: Role) -> Role:
        raise NotImplementedError

    async def get(self, role_id: RoleId) -> Role | None:
        raise NotImplementedError

    async def get_by_name(self, name: RoleName) -> Role | None:
        raise NotImplementedError

    async def list(self) -> Sequence[Role]:
        raise NotImplementedError

    async def update(self, role: Role) -> Role:
        raise NotImplementedError

    async def add_permission(self, role_id: RoleId, permission_id: PermissionId) -> None:
        raise NotImplementedError

    async def set_permissions(
        self,
        role_id: RoleId,
        permission_ids: Sequence[PermissionId],
    ) -> None:
        raise NotImplementedError

    async def list_permissions(self, role_id: RoleId) -> Sequence[Permission]:
        raise NotImplementedError

    async def has_permission(self, role_id: RoleId, permission_id: PermissionId) -> bool:
        raise NotImplementedError

    async def count_assignments(self, role_id: RoleId) -> int:
        raise NotImplementedError


class RoleAssignmentRepository(Protocol):
    async def create(self, role_assignment: RoleAssignment) -> RoleAssignment:
        raise NotImplementedError

    async def list_for_identity(
        self,
        identity_id: UserId | ServiceAccountId,
        identity_type: ApiKeyOwnerType,
    ) -> Sequence[RoleAssignment]:
        raise NotImplementedError

    async def get_for_identity_scope_role(
        self,
        identity_id: UserId | ServiceAccountId,
        identity_type: ApiKeyOwnerType,
        scope_type: ScopeType,
        scope_id: UUID | None,
        role_id: RoleId,
    ) -> RoleAssignment | None:
        raise NotImplementedError

    async def delete(self, role_assignment_id: RoleAssignmentId) -> None:
        raise NotImplementedError

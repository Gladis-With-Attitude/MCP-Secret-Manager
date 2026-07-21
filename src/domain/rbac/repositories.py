from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from domain.identity.value_objects import ApiKeyOwnerType, ServiceAccountId, UserId
from domain.rbac.entities import Permission, Role, RoleAssignment
from domain.rbac.value_objects import PermissionId, PermissionName, RoleId, RoleName


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


class RoleRepository(Protocol):
    async def create(self, role: Role) -> Role:
        raise NotImplementedError

    async def get(self, role_id: RoleId) -> Role | None:
        raise NotImplementedError

    async def get_by_name(self, name: RoleName) -> Role | None:
        raise NotImplementedError

    async def add_permission(self, role_id: RoleId, permission_id: PermissionId) -> None:
        raise NotImplementedError

    async def has_permission(self, role_id: RoleId, permission_id: PermissionId) -> bool:
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

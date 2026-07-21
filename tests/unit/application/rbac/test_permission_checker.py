from __future__ import annotations

from collections.abc import Sequence
from types import TracebackType
from typing import Self
from uuid import UUID

import anyio
import pytest

from application.rbac.dto import RequirePermission
from application.rbac.exceptions import AuthorizationDeniedError
from application.rbac.use_cases import AuthorizeUseCase, PermissionChecker
from domain.identity.value_objects import ApiKeyOwnerType, ServiceAccountId, UserId
from domain.rbac.entities import Permission, Role, RoleAssignment
from domain.rbac.repositories import (
    PermissionRepository,
    PermissionRepositoryConflictError,
    RoleAssignmentRepository,
    RoleAssignmentRepositoryConflictError,
    RoleRepository,
    RoleRepositoryConflictError,
)
from domain.rbac.value_objects import PermissionId, PermissionName, RoleId, RoleName, ScopeType


class InMemoryPermissionRepository:
    def __init__(self) -> None:
        self._permissions: dict[PermissionId, Permission] = {}

    async def create(self, permission: Permission) -> Permission:
        if await self.get_by_name(permission.name) is not None:
            raise PermissionRepositoryConflictError("Permission already exists.")
        self._permissions[permission.id] = permission
        return permission

    async def get(self, permission_id: PermissionId) -> Permission | None:
        return self._permissions.get(permission_id)

    async def get_by_name(self, name: PermissionName) -> Permission | None:
        return next(
            (permission for permission in self._permissions.values() if permission.name == name),
            None,
        )


class InMemoryRoleRepository:
    def __init__(self) -> None:
        self._roles: dict[RoleId, Role] = {}
        self._role_permissions: set[tuple[RoleId, PermissionId]] = set()

    async def create(self, role: Role) -> Role:
        if await self.get_by_name(role.name) is not None:
            raise RoleRepositoryConflictError("Role already exists.")
        self._roles[role.id] = role
        return role

    async def get(self, role_id: RoleId) -> Role | None:
        return self._roles.get(role_id)

    async def get_by_name(self, name: RoleName) -> Role | None:
        return next((role for role in self._roles.values() if role.name == name), None)

    async def add_permission(self, role_id: RoleId, permission_id: PermissionId) -> None:
        self._role_permissions.add((role_id, permission_id))

    async def has_permission(self, role_id: RoleId, permission_id: PermissionId) -> bool:
        return (role_id, permission_id) in self._role_permissions


class InMemoryRoleAssignmentRepository:
    def __init__(self) -> None:
        self._assignments: dict[str, RoleAssignment] = {}

    async def create(self, role_assignment: RoleAssignment) -> RoleAssignment:
        key = (
            f"{role_assignment.identity_type}:"
            f"{role_assignment.identity_id}:"
            f"{role_assignment.scope_type}:"
            f"{role_assignment.scope_id}:"
            f"{role_assignment.role_id}"
        )
        if key in self._assignments:
            raise RoleAssignmentRepositoryConflictError("Role assignment already exists.")
        self._assignments[key] = role_assignment
        return role_assignment

    async def list_for_identity(
        self,
        identity_id: UserId | ServiceAccountId,
        identity_type: ApiKeyOwnerType,
    ) -> Sequence[RoleAssignment]:
        return tuple(
            assignment
            for assignment in self._assignments.values()
            if assignment.identity_id == identity_id and assignment.identity_type == identity_type
        )


class InMemoryRbacUnitOfWork:
    def __init__(self) -> None:
        self._permissions = InMemoryPermissionRepository()
        self._roles = InMemoryRoleRepository()
        self._role_assignments = InMemoryRoleAssignmentRepository()

    @property
    def permissions(self) -> PermissionRepository:
        return self._permissions

    @property
    def roles(self) -> RoleRepository:
        return self._roles

    @property
    def role_assignments(self) -> RoleAssignmentRepository:
        return self._role_assignments

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None

    async def commit(self) -> None:
        return None

    async def rollback(self) -> None:
        return None


async def grant_role(
    unit_of_work: InMemoryRbacUnitOfWork,
    identity_id: UserId | ServiceAccountId,
    identity_type: ApiKeyOwnerType,
    permission_name: str,
    scope_type: ScopeType,
    scope_id: UUID | None,
    role_name: str = "reader",
) -> None:
    permission = await unit_of_work.permissions.create(
        Permission.create(PermissionName(permission_name), "Test permission.")
    )
    role = await unit_of_work.roles.create(Role.create(RoleName(role_name), "Test role."))
    await unit_of_work.roles.add_permission(role.id, permission.id)
    await unit_of_work.role_assignments.create(
        RoleAssignment.create(identity_id, identity_type, scope_type, scope_id, role.id)
    )


async def is_allowed(unit_of_work: InMemoryRbacUnitOfWork, request: RequirePermission) -> bool:
    return await PermissionChecker(unit_of_work).is_allowed(request)


def test_permission_checker_allows_matching_project_permission_for_user() -> None:
    async def run() -> None:
        unit_of_work = InMemoryRbacUnitOfWork()
        user_id = UserId.new()
        project_id = UUID("1e423965-794a-49d5-8272-36c78dcf3e70")
        await grant_role(
            unit_of_work,
            user_id,
            ApiKeyOwnerType.USER,
            "secret.read",
            ScopeType.PROJECT,
            project_id,
        )

        allowed = await is_allowed(
            unit_of_work,
            RequirePermission(str(user_id), "user", "secret.read", "project", str(project_id)),
        )

        assert allowed is True

    anyio.run(run)


def test_permission_checker_denies_missing_permission() -> None:
    async def run() -> None:
        unit_of_work = InMemoryRbacUnitOfWork()
        user_id = UserId.new()
        project_id = UUID("1e423965-794a-49d5-8272-36c78dcf3e70")
        await grant_role(
            unit_of_work,
            user_id,
            ApiKeyOwnerType.USER,
            "secret.read",
            ScopeType.PROJECT,
            project_id,
        )

        allowed = await is_allowed(
            unit_of_work,
            RequirePermission(str(user_id), "user", "secret.decrypt", "project", str(project_id)),
        )

        assert allowed is False

    anyio.run(run)


def test_authorize_use_case_raises_when_permission_is_denied() -> None:
    async def run() -> None:
        unit_of_work = InMemoryRbacUnitOfWork()
        user_id = UserId.new()

        with pytest.raises(AuthorizationDeniedError):
            await AuthorizeUseCase(PermissionChecker(unit_of_work)).execute(
                RequirePermission(str(user_id), "user", "vault.read", "global")
            )

    anyio.run(run)


def test_global_scope_grant_applies_to_project_scope() -> None:
    async def run() -> None:
        unit_of_work = InMemoryRbacUnitOfWork()
        user_id = UserId.new()
        await grant_role(
            unit_of_work,
            user_id,
            ApiKeyOwnerType.USER,
            "project.read",
            ScopeType.GLOBAL,
            None,
        )

        allowed = await is_allowed(
            unit_of_work,
            RequirePermission(
                str(user_id),
                "user",
                "project.read",
                "project",
                "1e423965-794a-49d5-8272-36c78dcf3e70",
            ),
        )

        assert allowed is True

    anyio.run(run)


def test_vault_scope_grant_inherits_to_project_scope() -> None:
    async def run() -> None:
        unit_of_work = InMemoryRbacUnitOfWork()
        service_account_id = ServiceAccountId.new()
        vault_id = UUID("9d14f3b1-38cc-4447-b69e-e7286fc59d1f")
        project_id = UUID("1e423965-794a-49d5-8272-36c78dcf3e70")
        await grant_role(
            unit_of_work,
            service_account_id,
            ApiKeyOwnerType.SERVICE_ACCOUNT,
            "secret.read",
            ScopeType.VAULT,
            vault_id,
        )

        allowed = await is_allowed(
            unit_of_work,
            RequirePermission(
                str(service_account_id),
                "service_account",
                "secret.read",
                "project",
                str(project_id),
                parent_vault_id=str(vault_id),
            ),
        )

        assert allowed is True

    anyio.run(run)


def test_vault_scope_grant_does_not_apply_to_unrelated_project() -> None:
    async def run() -> None:
        unit_of_work = InMemoryRbacUnitOfWork()
        service_account_id = ServiceAccountId.new()
        vault_id = UUID("9d14f3b1-38cc-4447-b69e-e7286fc59d1f")
        await grant_role(
            unit_of_work,
            service_account_id,
            ApiKeyOwnerType.SERVICE_ACCOUNT,
            "secret.read",
            ScopeType.VAULT,
            vault_id,
        )

        allowed = await is_allowed(
            unit_of_work,
            RequirePermission(
                str(service_account_id),
                "service_account",
                "secret.read",
                "project",
                "1e423965-794a-49d5-8272-36c78dcf3e70",
                parent_vault_id="aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa",
            ),
        )

        assert allowed is False

    anyio.run(run)


def test_project_scope_grant_prepares_secret_scope_inheritance() -> None:
    async def run() -> None:
        unit_of_work = InMemoryRbacUnitOfWork()
        user_id = UserId.new()
        project_id = UUID("1e423965-794a-49d5-8272-36c78dcf3e70")
        secret_id = UUID("a9dbdc7a-890a-4f69-af0c-5dd899239631")
        await grant_role(
            unit_of_work,
            user_id,
            ApiKeyOwnerType.USER,
            "secret.decrypt",
            ScopeType.PROJECT,
            project_id,
        )

        allowed = await is_allowed(
            unit_of_work,
            RequirePermission(
                str(user_id),
                "user",
                "secret.decrypt",
                "secret",
                str(secret_id),
                parent_project_id=str(project_id),
            ),
        )

        assert allowed is True

    anyio.run(run)


def test_multiple_roles_allow_union_of_permissions() -> None:
    async def run() -> None:
        unit_of_work = InMemoryRbacUnitOfWork()
        user_id = UserId.new()
        project_id = UUID("1e423965-794a-49d5-8272-36c78dcf3e70")
        await grant_role(
            unit_of_work,
            user_id,
            ApiKeyOwnerType.USER,
            "secret.read",
            ScopeType.PROJECT,
            project_id,
            role_name="reader",
        )
        await grant_role(
            unit_of_work,
            user_id,
            ApiKeyOwnerType.USER,
            "secret.rotate",
            ScopeType.PROJECT,
            project_id,
            role_name="rotator",
        )

        allowed = await is_allowed(
            unit_of_work,
            RequirePermission(str(user_id), "user", "secret.rotate", "project", str(project_id)),
        )

        assert allowed is True

    anyio.run(run)

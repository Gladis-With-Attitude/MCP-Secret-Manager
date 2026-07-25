from __future__ import annotations

from collections.abc import Sequence
from types import TracebackType
from typing import Self
from uuid import UUID

import anyio
import pytest

from application.rbac.dto import (
    AssignActorRoleRequest,
    CreateRoleRequest,
    ListActorRolesRequest,
    ListRolesRequest,
    RequirePermission,
    RevokeActorRoleRequest,
    UpdateRoleRequest,
)
from application.rbac.exceptions import AuthorizationDeniedError, RbacValidationError
from application.rbac.use_cases import (
    AssignActorRoleUseCase,
    AuthorizeUseCase,
    CreateRoleUseCase,
    ListActorRolesUseCase,
    ListRolesUseCase,
    PermissionChecker,
    RevokeActorRoleUseCase,
    UpdateRoleUseCase,
)
from domain.audit.entities import AuditEvent
from domain.identity.entities import ServiceAccount, User
from domain.identity.repositories import ServiceAccountRepository, UserRepository
from domain.identity.value_objects import (
    ApiKeyOwnerType,
    ServiceAccountId,
    ServiceAccountName,
    UserDisplayName,
    UserEmail,
    UserId,
)
from domain.project.value_objects import ProjectId
from domain.rbac.entities import Permission, Role, RoleAssignment
from domain.rbac.repositories import (
    PermissionRepository,
    PermissionRepositoryConflictError,
    RoleAssignmentRepository,
    RoleAssignmentRepositoryConflictError,
    RoleRepository,
    RoleRepositoryConflictError,
)
from domain.rbac.value_objects import (
    PermissionId,
    PermissionName,
    RoleAssignmentId,
    RoleId,
    RoleName,
    ScopeType,
)


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

    async def list(self) -> Sequence[Permission]:
        return tuple(
            sorted(self._permissions.values(), key=lambda permission: permission.name.value)
        )


class InMemoryRoleRepository:
    def __init__(self, permissions: InMemoryPermissionRepository) -> None:
        self._permissions = permissions
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

    async def list(self) -> Sequence[Role]:
        return tuple(sorted(self._roles.values(), key=lambda role: role.name.value))

    async def update(self, role: Role) -> Role:
        self._roles[role.id] = role
        return role

    async def add_permission(self, role_id: RoleId, permission_id: PermissionId) -> None:
        self._role_permissions.add((role_id, permission_id))

    async def set_permissions(
        self,
        role_id: RoleId,
        permission_ids: Sequence[PermissionId],
    ) -> None:
        self._role_permissions = {item for item in self._role_permissions if item[0] != role_id}
        for permission_id in permission_ids:
            self._role_permissions.add((role_id, permission_id))

    async def list_permissions(self, role_id: RoleId) -> Sequence[Permission]:
        permission_ids = {
            permission_id
            for assigned_role_id, permission_id in self._role_permissions
            if assigned_role_id == role_id
        }
        return tuple(
            sorted(
                (
                    permission
                    for permission in self._permissions._permissions.values()
                    if permission.id in permission_ids
                ),
                key=lambda permission: permission.name.value,
            )
        )

    async def has_permission(self, role_id: RoleId, permission_id: PermissionId) -> bool:
        return (role_id, permission_id) in self._role_permissions

    async def count_assignments(self, _role_id: RoleId) -> int:
        return 0


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

    async def get_for_identity_scope_role(
        self,
        identity_id: UserId | ServiceAccountId,
        identity_type: ApiKeyOwnerType,
        scope_type: ScopeType,
        scope_id: UUID | None,
        role_id: RoleId,
    ) -> RoleAssignment | None:
        return next(
            (
                assignment
                for assignment in self._assignments.values()
                if assignment.identity_id == identity_id
                and assignment.identity_type == identity_type
                and assignment.scope_type == scope_type
                and assignment.scope_id == scope_id
                and assignment.role_id == role_id
            ),
            None,
        )

    async def delete(self, role_assignment_id: RoleAssignmentId) -> None:
        self._assignments = {
            key: assignment
            for key, assignment in self._assignments.items()
            if assignment.id != role_assignment_id
        }


class InMemoryUserRepository:
    def __init__(self) -> None:
        self._users: dict[UserId, User] = {}

    async def create(self, user: User) -> User:
        self._users[user.id] = user
        return user

    async def get(self, user_id: UserId) -> User | None:
        return self._users.get(user_id)

    async def get_by_email(self, email: UserEmail) -> User | None:
        return next((user for user in self._users.values() if user.email == email), None)

    async def update(self, user: User) -> User:
        self._users[user.id] = user
        return user


class EmptyServiceAccountRepository:
    async def create(self, service_account: ServiceAccount) -> ServiceAccount:
        return service_account

    async def get(self, _service_account_id: ServiceAccountId) -> ServiceAccount | None:
        return None

    async def exists_in_project(self, _project_id: ProjectId, _name: ServiceAccountName) -> bool:
        return False


class InMemoryRbacUnitOfWork:
    def __init__(self) -> None:
        self._permissions = InMemoryPermissionRepository()
        self._roles = InMemoryRoleRepository(self._permissions)
        self._role_assignments = InMemoryRoleAssignmentRepository()
        self._users = InMemoryUserRepository()
        self._service_accounts = EmptyServiceAccountRepository()

    @property
    def permissions(self) -> PermissionRepository:
        return self._permissions

    @property
    def roles(self) -> RoleRepository:
        return self._roles

    @property
    def role_assignments(self) -> RoleAssignmentRepository:
        return self._role_assignments

    @property
    def users(self) -> UserRepository:
        return self._users

    @property
    def service_accounts(self) -> ServiceAccountRepository:
        return self._service_accounts

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


class RecordingAuditRecorder:
    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    async def record(self, event: AuditEvent) -> None:
        self.events.append(event)


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
        audit_recorder = RecordingAuditRecorder()

        with pytest.raises(AuthorizationDeniedError):
            await AuthorizeUseCase(
                PermissionChecker(unit_of_work),
                audit_recorder=audit_recorder,
            ).execute(
                RequirePermission(
                    str(user_id),
                    "user",
                    "vault.read",
                    "global",
                    ip_address="127.0.0.1",
                    user_agent="test-client",
                    request_id="req-1",
                )
            )

        assert len(audit_recorder.events) == 1
        event = audit_recorder.events[0]
        assert event.action.value == "permission.denied"
        assert event.result.value == "FAILURE"
        assert event.actor_id == str(user_id)
        assert event.metadata == {"permission": "vault.read", "protocol": "rest"}

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


def test_role_management_use_cases_create_update_and_list_custom_roles() -> None:
    async def run() -> None:
        unit_of_work = InMemoryRbacUnitOfWork()
        secret_read = await unit_of_work.permissions.create(
            Permission.create(PermissionName("secret.read"), "Read secret metadata.")
        )
        secret_rotate = await unit_of_work.permissions.create(
            Permission.create(PermissionName("secret.rotate"), "Rotate secrets.")
        )

        created = await CreateRoleUseCase(unit_of_work).execute(
            CreateRoleRequest(
                name="secret-operator",
                description="Manage secret metadata.",
                permission_ids=(str(secret_read.id), str(secret_read.id)),
            )
        )
        assert created.name == "secret-operator"
        assert created.permission_ids == (str(secret_read.id),)
        assert created.permissions_count == 1
        assert created.ui_permissions.update is True

        updated = await UpdateRoleUseCase(unit_of_work).execute(
            UpdateRoleRequest(
                role_id=created.id,
                name="secret-rotator",
                description="Rotate secret metadata.",
                permission_ids=(str(secret_rotate.id),),
            )
        )
        assert updated.name == "secret-rotator"
        assert updated.permission_ids == (str(secret_rotate.id),)

        listed = await ListRolesUseCase(unit_of_work).execute(
            ListRolesRequest(search="rotator", kind="custom")
        )
        assert listed.total == 1
        assert listed.data[0].id == created.id

    anyio.run(run)


def test_role_management_rejects_system_role_update() -> None:
    async def run() -> None:
        unit_of_work = InMemoryRbacUnitOfWork()
        role = await unit_of_work.roles.create(
            Role.create(RoleName("administrator"), "System administrator.")
        )

        with pytest.raises(RbacValidationError, match="System roles cannot be updated"):
            await UpdateRoleUseCase(unit_of_work).execute(
                UpdateRoleRequest(
                    role_id=str(role.id),
                    name="administrator",
                    description="Changed.",
                    permission_ids=(),
                )
            )

    anyio.run(run)


def test_actor_role_use_cases_assign_list_and_revoke_user_roles() -> None:
    async def run() -> None:
        unit_of_work = InMemoryRbacUnitOfWork()
        user = await unit_of_work.users.create(
            User.create(
                email=UserEmail("assignee@example.test"),
                display_name=UserDisplayName("Assignee"),
            )
        )
        role = await unit_of_work.roles.create(Role.create(RoleName("reader"), "Read data."))

        assigned = await AssignActorRoleUseCase(unit_of_work).execute(
            AssignActorRoleRequest(actor_id=str(user.id), role_id=str(role.id))
        )
        assert assigned.actor_id == str(user.id)
        assert assigned.role_id == str(role.id)
        assert assigned.role_name == "reader"

        listed = await ListActorRolesUseCase(unit_of_work).execute(
            ListActorRolesRequest(actor_id=str(user.id))
        )
        assert [assignment.role_id for assignment in listed.data] == [str(role.id)]

        revoked = await RevokeActorRoleUseCase(unit_of_work).execute(
            RevokeActorRoleRequest(actor_id=str(user.id), role_id=str(role.id))
        )
        assert revoked.id == assigned.id
        assert revoked.status == "revoked"

        remaining = await ListActorRolesUseCase(unit_of_work).execute(
            ListActorRolesRequest(actor_id=str(user.id))
        )
        assert remaining.data == ()

    anyio.run(run)

from __future__ import annotations

from uuid import UUID

from application.audit.dto import AuditContext
from application.audit.use_cases import NoopAuditRecorder, record_audit_event
from application.rbac.dto import (
    AssignActorRoleRequest,
    AuthorizationDecision,
    CreateRoleRequest,
    GetRoleRequest,
    ListActorRolesRequest,
    ListRolesRequest,
    PermissionListResponse,
    PermissionResponse,
    RequirePermission,
    RevokeActorRoleRequest,
    RoleListResponse,
    RolePermissionsResponse,
    RoleResponse,
    UpdateRoleRequest,
    UserRoleListResponse,
    UserRoleResponse,
)
from application.rbac.exceptions import (
    AuthorizationDeniedError,
    RbacConflictError,
    RbacNotFoundError,
    RbacValidationError,
)
from application.rbac.unit_of_work import RbacUnitOfWork
from domain.audit.repositories import AuditRecorder
from domain.audit.value_objects import AuditResult
from domain.identity.value_objects import ApiKeyOwnerType, IdentityStatus, ServiceAccountId, UserId
from domain.rbac.entities import Permission, Role, RoleAssignment
from domain.rbac.exceptions import RbacDomainError
from domain.rbac.repositories import (
    RoleAssignmentRepositoryConflictError,
    RoleRepositoryConflictError,
)
from domain.rbac.value_objects import PermissionId, PermissionName, RoleId, RoleName, ScopeType

SYSTEM_ROLE_NAMES = frozenset({"administrator", "user", "readonly"})
ROLE_ACTION_PERMISSIONS = RolePermissionsResponse(
    assign=True,
    create=True,
    read=True,
    revoke=True,
    update=True,
)
CRITICAL_PERMISSION_PATTERN = frozenset(
    {"archive", "create", "delete", "decrypt", "revoke", "rotate", "update"}
)


class PermissionChecker:
    def __init__(self, unit_of_work: RbacUnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def is_allowed(self, request: RequirePermission) -> bool:
        identity_type = self._validate_identity_type(request.identity_type)
        identity_id = self._validate_identity_id(request.identity_id, identity_type)
        permission_name = self._validate_permission_name(request.permission)
        scope_type = self._validate_scope_type(request.scope_type)
        scope_id = self._validate_optional_uuid(request.scope_id, field_name="scope id")
        parent_vault_id = self._validate_optional_uuid(
            request.parent_vault_id,
            field_name="parent vault id",
        )
        parent_project_id = self._validate_optional_uuid(
            request.parent_project_id,
            field_name="parent project id",
        )

        async with self._unit_of_work as unit_of_work:
            permission = await unit_of_work.permissions.get_by_name(permission_name)
            if permission is None:
                return False

            assignments = await unit_of_work.role_assignments.list_for_identity(
                identity_id,
                identity_type,
            )
            for assignment in assignments:
                if not self._scope_applies(
                    assignment,
                    scope_type,
                    scope_id,
                    parent_vault_id,
                    parent_project_id,
                ):
                    continue
                if await unit_of_work.roles.has_permission(assignment.role_id, permission.id):
                    return True

        return False

    @staticmethod
    def _scope_applies(
        assignment: RoleAssignment,
        requested_scope_type: ScopeType,
        requested_scope_id: UUID | None,
        parent_vault_id: UUID | None,
        parent_project_id: UUID | None,
    ) -> bool:
        if assignment.scope_type is ScopeType.GLOBAL:
            return True
        if requested_scope_type is ScopeType.GLOBAL:
            return False
        if assignment.scope_type is requested_scope_type:
            return assignment.scope_id == requested_scope_id
        if assignment.scope_type is ScopeType.VAULT and requested_scope_type is ScopeType.PROJECT:
            return assignment.scope_id == parent_vault_id
        if (
            assignment.scope_type is ScopeType.VAULT
            and requested_scope_type is ScopeType.SECRET_RESOURCE
        ):
            return assignment.scope_id == parent_vault_id
        if (
            assignment.scope_type is ScopeType.PROJECT
            and requested_scope_type is ScopeType.SECRET_RESOURCE
        ):
            return assignment.scope_id == parent_project_id
        return False

    @staticmethod
    def _validate_identity_type(raw_identity_type: str) -> ApiKeyOwnerType:
        try:
            return ApiKeyOwnerType(raw_identity_type)
        except ValueError as exc:
            raise RbacValidationError("Identity type is invalid.") from exc

    @staticmethod
    def _validate_identity_id(
        raw_identity_id: str,
        identity_type: ApiKeyOwnerType,
    ) -> UserId | ServiceAccountId:
        try:
            if identity_type is ApiKeyOwnerType.USER:
                return UserId.from_string(raw_identity_id)
            return ServiceAccountId.from_string(raw_identity_id)
        except ValueError as exc:
            raise RbacValidationError("Identity id must be a valid UUID.") from exc

    @staticmethod
    def _validate_permission_name(raw_permission: str) -> PermissionName:
        try:
            return PermissionName(raw_permission)
        except RbacDomainError as exc:
            raise RbacValidationError(str(exc)) from exc

    @staticmethod
    def _validate_scope_type(raw_scope_type: str) -> ScopeType:
        try:
            return ScopeType(raw_scope_type)
        except ValueError as exc:
            raise RbacValidationError("Scope type is invalid.") from exc

    @staticmethod
    def _validate_optional_uuid(raw_value: str | None, field_name: str) -> UUID | None:
        if raw_value is None:
            return None
        try:
            return UUID(raw_value)
        except ValueError as exc:
            raise RbacValidationError(f"{field_name.capitalize()} must be a valid UUID.") from exc


class AuthorizeUseCase:
    def __init__(
        self,
        permission_checker: PermissionChecker,
        audit_recorder: AuditRecorder | None = None,
    ) -> None:
        self._permission_checker = permission_checker
        self._audit_recorder = audit_recorder or NoopAuditRecorder()

    async def execute(self, request: RequirePermission) -> AuthorizationDecision:
        allowed = await self._permission_checker.is_allowed(request)
        if not allowed:
            await record_audit_event(
                self._audit_recorder,
                AuditContext(
                    actor_id=request.identity_id,
                    actor_type=request.identity_type,
                    ip_address=request.ip_address,
                    user_agent=request.user_agent,
                    request_id=request.request_id,
                ),
                action="permission.denied",
                resource_type=request.scope_type,
                resource_id=request.scope_id,
                result=AuditResult.FAILURE,
                metadata={"permission": request.permission},
            )
            raise AuthorizationDeniedError("Permission denied.")
        return AuthorizationDecision(allowed=True)


class ListPermissionsUseCase:
    def __init__(self, unit_of_work: RbacUnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def execute(self) -> PermissionListResponse:
        async with self._unit_of_work as unit_of_work:
            permissions = await unit_of_work.permissions.list()

        return PermissionListResponse(
            data=tuple(_permission_response(permission) for permission in permissions)
        )


class ListRolesUseCase:
    def __init__(self, unit_of_work: RbacUnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def execute(self, request: ListRolesRequest) -> RoleListResponse:
        limit = _validate_limit(request.limit)
        offset = _validate_offset(request.offset)
        kind = _validate_kind(request.kind)
        status = _validate_status(request.status)
        search = request.search.strip().lower() if request.search else None

        async with self._unit_of_work as unit_of_work:
            roles = tuple(await unit_of_work.roles.list())
            filtered = tuple(
                role
                for role in roles
                if _matches_role_filters(role, kind=kind, status=status, search=search)
            )
            page = filtered[offset : offset + limit]
            responses = tuple([await _role_response(unit_of_work, role) for role in page])

        return RoleListResponse(
            data=responses,
            limit=limit,
            offset=offset,
            total=len(filtered),
            permissions=ROLE_ACTION_PERMISSIONS,
        )


class GetRoleUseCase:
    def __init__(
        self,
        unit_of_work: RbacUnitOfWork,
        audit_recorder: AuditRecorder | None = None,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._audit_recorder = audit_recorder or NoopAuditRecorder()

    async def execute(self, request: GetRoleRequest) -> RoleResponse:
        role_id = _validate_role_id(request.role_id)
        async with self._unit_of_work as unit_of_work:
            role = await unit_of_work.roles.get(role_id)
            if role is None:
                raise RbacNotFoundError("Role not found.")
            response = await _role_response(unit_of_work, role)

        await record_audit_event(
            self._audit_recorder,
            request.audit_context,
            action="role.read",
            resource_type="role",
            resource_id=request.role_id,
            result=AuditResult.SUCCESS,
        )
        return response


class CreateRoleUseCase:
    def __init__(
        self,
        unit_of_work: RbacUnitOfWork,
        audit_recorder: AuditRecorder | None = None,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._audit_recorder = audit_recorder or NoopAuditRecorder()

    async def execute(self, request: CreateRoleRequest) -> RoleResponse:
        name = _validate_role_name(request.name)
        description = _validate_description(request.description)
        permission_ids = _validate_permission_ids(request.permission_ids)

        async with self._unit_of_work as unit_of_work:
            if await unit_of_work.roles.get_by_name(name) is not None:
                raise RbacConflictError("A role with this name already exists.")
            await _ensure_permissions_exist(unit_of_work, permission_ids)
            try:
                role = await unit_of_work.roles.create(Role.create(name, description))
                await unit_of_work.roles.set_permissions(role.id, permission_ids)
            except RoleRepositoryConflictError as exc:
                raise RbacConflictError("Role persistence conflict.") from exc
            await unit_of_work.commit()
            response = await _role_response(unit_of_work, role)

        await record_audit_event(
            self._audit_recorder,
            request.audit_context,
            action="role.create",
            resource_type="role",
            resource_id=response.id,
            result=AuditResult.SUCCESS,
            metadata={"permission_count": response.permissions_count},
        )
        return response


class UpdateRoleUseCase:
    def __init__(
        self,
        unit_of_work: RbacUnitOfWork,
        audit_recorder: AuditRecorder | None = None,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._audit_recorder = audit_recorder or NoopAuditRecorder()

    async def execute(self, request: UpdateRoleRequest) -> RoleResponse:
        role_id = _validate_role_id(request.role_id)
        name = _validate_role_name(request.name)
        description = _validate_description(request.description)
        permission_ids = _validate_permission_ids(request.permission_ids)

        async with self._unit_of_work as unit_of_work:
            current = await unit_of_work.roles.get(role_id)
            if current is None:
                raise RbacNotFoundError("Role not found.")
            if _is_system_role(current):
                raise RbacValidationError("System roles cannot be updated.")
            existing = await unit_of_work.roles.get_by_name(name)
            if existing is not None and existing.id != current.id:
                raise RbacConflictError("A role with this name already exists.")
            await _ensure_permissions_exist(unit_of_work, permission_ids)
            updated = Role(id=current.id, name=name, description=description)
            try:
                persisted = await unit_of_work.roles.update(updated)
                await unit_of_work.roles.set_permissions(persisted.id, permission_ids)
            except RoleRepositoryConflictError as exc:
                raise RbacConflictError("Role persistence conflict.") from exc
            await unit_of_work.commit()
            response = await _role_response(unit_of_work, persisted)

        await record_audit_event(
            self._audit_recorder,
            request.audit_context,
            action="role.update",
            resource_type="role",
            resource_id=response.id,
            result=AuditResult.SUCCESS,
            metadata={"permission_count": response.permissions_count},
        )
        return response


class ListActorRolesUseCase:
    def __init__(self, unit_of_work: RbacUnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def execute(self, request: ListActorRolesRequest) -> UserRoleListResponse:
        identity_type = _validate_identity_type(request.identity_type)
        identity_id = _validate_identity_id(request.actor_id, identity_type)

        async with self._unit_of_work as unit_of_work:
            await _ensure_actor_exists(unit_of_work, identity_id, identity_type)
            assignments = await unit_of_work.role_assignments.list_for_identity(
                identity_id,
                identity_type,
            )
            responses = tuple(
                [await _assignment_response(unit_of_work, assignment) for assignment in assignments]
            )

        return UserRoleListResponse(
            actor_id=request.actor_id,
            data=responses,
            permissions=ROLE_ACTION_PERMISSIONS,
        )


class AssignActorRoleUseCase:
    def __init__(
        self,
        unit_of_work: RbacUnitOfWork,
        audit_recorder: AuditRecorder | None = None,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._audit_recorder = audit_recorder or NoopAuditRecorder()

    async def execute(self, request: AssignActorRoleRequest) -> UserRoleResponse:
        identity_type = _validate_identity_type(request.identity_type)
        identity_id = _validate_identity_id(request.actor_id, identity_type)
        role_id = _validate_role_id(request.role_id)

        async with self._unit_of_work as unit_of_work:
            await _ensure_actor_exists(unit_of_work, identity_id, identity_type)
            role = await unit_of_work.roles.get(role_id)
            if role is None:
                raise RbacNotFoundError("Role not found.")
            assignment = RoleAssignment.create(
                identity_id=identity_id,
                identity_type=identity_type,
                scope_type=ScopeType.GLOBAL,
                scope_id=None,
                role_id=role.id,
            )
            try:
                created = await unit_of_work.role_assignments.create(assignment)
            except RoleAssignmentRepositoryConflictError as exc:
                raise RbacConflictError("Role is already assigned to this actor.") from exc
            await unit_of_work.commit()
            response = await _assignment_response(unit_of_work, created)

        await record_audit_event(
            self._audit_recorder,
            request.audit_context,
            action="role.assign",
            resource_type="role_assignment",
            resource_id=response.id,
            result=AuditResult.SUCCESS,
            metadata={"actor_id": request.actor_id, "role_id": request.role_id},
        )
        return response


class RevokeActorRoleUseCase:
    def __init__(
        self,
        unit_of_work: RbacUnitOfWork,
        audit_recorder: AuditRecorder | None = None,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._audit_recorder = audit_recorder or NoopAuditRecorder()

    async def execute(self, request: RevokeActorRoleRequest) -> UserRoleResponse:
        identity_type = _validate_identity_type(request.identity_type)
        identity_id = _validate_identity_id(request.actor_id, identity_type)
        role_id = _validate_role_id(request.role_id)

        async with self._unit_of_work as unit_of_work:
            await _ensure_actor_exists(unit_of_work, identity_id, identity_type)
            assignment = await unit_of_work.role_assignments.get_for_identity_scope_role(
                identity_id,
                identity_type,
                ScopeType.GLOBAL,
                None,
                role_id,
            )
            if assignment is None:
                raise RbacNotFoundError("Role assignment not found.")
            response = await _assignment_response(unit_of_work, assignment, status="revoked")
            await unit_of_work.role_assignments.delete(assignment.id)
            await unit_of_work.commit()

        await record_audit_event(
            self._audit_recorder,
            request.audit_context,
            action="role.revoke",
            resource_type="role_assignment",
            resource_id=response.id,
            result=AuditResult.SUCCESS,
            metadata={"actor_id": request.actor_id, "role_id": request.role_id},
        )
        return response


def _permission_response(permission: Permission) -> PermissionResponse:
    resource, _, action = permission.name.value.partition(".")
    action = action or "access"
    sensitivity = "critical" if action in CRITICAL_PERMISSION_PATTERN else "standard"
    return PermissionResponse(
        id=str(permission.id),
        name=permission.name.value,
        description=permission.description,
        resource=resource or "system",
        action=action,
        group=resource or "system",
        sensitivity=sensitivity,
    )


async def _role_response(unit_of_work: RbacUnitOfWork, role: Role) -> RoleResponse:
    permissions = tuple(await unit_of_work.roles.list_permissions(role.id))
    permission_responses = tuple(_permission_response(permission) for permission in permissions)
    is_system = _is_system_role(role)
    ui_permissions = RolePermissionsResponse(
        assign=True,
        create=True,
        read=True,
        revoke=True,
        update=not is_system,
    )
    return RoleResponse(
        id=str(role.id),
        name=role.name.value,
        description=role.description,
        kind="system" if is_system else "custom",
        is_system=is_system,
        permission_ids=tuple(str(permission.id) for permission in permissions),
        permissions=permission_responses,
        permissions_count=len(permission_responses),
        assignments_count=await unit_of_work.roles.count_assignments(role.id),
        status="active",
        ui_permissions=ui_permissions,
    )


async def _assignment_response(
    unit_of_work: RbacUnitOfWork,
    assignment: RoleAssignment,
    status: str = "active",
) -> UserRoleResponse:
    role = await unit_of_work.roles.get(assignment.role_id)
    role_name = role.name.value if role is not None else str(assignment.role_id)
    return UserRoleResponse(
        id=str(assignment.id),
        actor_id=str(assignment.identity_id),
        role_id=str(assignment.role_id),
        role_name=role_name,
        scope_type=assignment.scope_type.value,
        scope_id=str(assignment.scope_id) if assignment.scope_id is not None else None,
        status=status,
        assigned_at=assignment.created_at.isoformat(),
    )


def _validate_limit(limit: int) -> int:
    if limit < 1 or limit > 100:
        raise RbacValidationError("Limit must be between 1 and 100.")
    return limit


def _validate_offset(offset: int) -> int:
    if offset < 0:
        raise RbacValidationError("Offset must be greater than or equal to 0.")
    return offset


def _validate_kind(raw_kind: str | None) -> str | None:
    if raw_kind is None or raw_kind.strip() == "":
        return None
    kind = raw_kind.strip().lower()
    if kind not in {"custom", "system"}:
        raise RbacValidationError("Role kind filter is invalid.")
    return kind


def _validate_status(raw_status: str | None) -> str | None:
    if raw_status is None or raw_status.strip() == "":
        return None
    status = raw_status.strip().lower()
    if status != "active":
        raise RbacValidationError("Role status filter is invalid.")
    return status


def _validate_role_name(raw_name: str) -> RoleName:
    try:
        return RoleName(raw_name)
    except RbacDomainError as exc:
        raise RbacValidationError(str(exc)) from exc


def _validate_description(raw_description: str | None) -> str | None:
    if raw_description is None:
        return None
    description = raw_description.strip()
    if not description:
        return None
    if len(description) > 1000:
        raise RbacValidationError("Role description must be 1000 characters or fewer.")
    return description


def _validate_permission_ids(raw_permission_ids: tuple[str, ...]) -> tuple[PermissionId, ...]:
    ids: list[PermissionId] = []
    seen: set[UUID] = set()
    for raw_permission_id in raw_permission_ids:
        try:
            permission_id = PermissionId.from_string(raw_permission_id)
        except ValueError as exc:
            raise RbacValidationError("Permission ids must be valid UUIDs.") from exc
        if permission_id.value in seen:
            continue
        seen.add(permission_id.value)
        ids.append(permission_id)
    return tuple(ids)


def _validate_role_id(raw_role_id: str) -> RoleId:
    try:
        return RoleId.from_string(raw_role_id)
    except ValueError as exc:
        raise RbacValidationError("Role id must be a valid UUID.") from exc


async def _ensure_permissions_exist(
    unit_of_work: RbacUnitOfWork,
    permission_ids: tuple[PermissionId, ...],
) -> None:
    for permission_id in permission_ids:
        if await unit_of_work.permissions.get(permission_id) is None:
            raise RbacNotFoundError("Permission not found.")


def _matches_role_filters(
    role: Role,
    *,
    kind: str | None,
    status: str | None,
    search: str | None,
) -> bool:
    if kind is not None and ("system" if _is_system_role(role) else "custom") != kind:
        return False
    if status is not None and status != "active":
        return False
    if search is None:
        return True
    return search in role.name.value.lower() or search in (role.description or "").lower()


def _is_system_role(role: Role) -> bool:
    return role.name.value in SYSTEM_ROLE_NAMES


def _validate_identity_type(raw_identity_type: str) -> ApiKeyOwnerType:
    try:
        return ApiKeyOwnerType(raw_identity_type)
    except ValueError as exc:
        raise RbacValidationError("Identity type is invalid.") from exc


def _validate_identity_id(
    raw_identity_id: str,
    identity_type: ApiKeyOwnerType,
) -> UserId | ServiceAccountId:
    try:
        if identity_type is ApiKeyOwnerType.USER:
            return UserId.from_string(raw_identity_id)
        return ServiceAccountId.from_string(raw_identity_id)
    except ValueError as exc:
        raise RbacValidationError("Actor id must be a valid UUID.") from exc


async def _ensure_actor_exists(
    unit_of_work: RbacUnitOfWork,
    identity_id: UserId | ServiceAccountId,
    identity_type: ApiKeyOwnerType,
) -> None:
    if identity_type is ApiKeyOwnerType.USER:
        if not isinstance(identity_id, UserId):
            raise RbacValidationError("Actor id must be a user id.")
        user = await unit_of_work.users.get(identity_id)
        if user is None or user.status is not IdentityStatus.ACTIVE:
            raise RbacNotFoundError("Actor not found.")
        return

    if not isinstance(identity_id, ServiceAccountId):
        raise RbacValidationError("Actor id must be a service account id.")
    service_account = await unit_of_work.service_accounts.get(identity_id)
    if service_account is None or service_account.status is not IdentityStatus.ACTIVE:
        raise RbacNotFoundError("Actor not found.")

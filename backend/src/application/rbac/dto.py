from __future__ import annotations

from dataclasses import dataclass

from application.audit.dto import AuditContext


@dataclass(frozen=True, slots=True)
class RequirePermission:
    identity_id: str
    identity_type: str
    permission: str
    scope_type: str
    scope_id: str | None = None
    parent_vault_id: str | None = None
    parent_project_id: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    request_id: str | None = None


@dataclass(frozen=True, slots=True)
class AuthorizationDecision:
    allowed: bool


@dataclass(frozen=True, slots=True)
class PermissionResponse:
    id: str
    name: str
    description: str | None
    resource: str
    action: str
    group: str
    sensitivity: str


@dataclass(frozen=True, slots=True)
class RolePermissionsResponse:
    assign: bool
    create: bool
    read: bool
    revoke: bool
    update: bool


@dataclass(frozen=True, slots=True)
class RoleResponse:
    id: str
    name: str
    description: str | None
    kind: str
    is_system: bool
    permission_ids: tuple[str, ...]
    permissions: tuple[PermissionResponse, ...]
    permissions_count: int
    assignments_count: int
    status: str
    ui_permissions: RolePermissionsResponse


@dataclass(frozen=True, slots=True)
class RoleListResponse:
    data: tuple[RoleResponse, ...]
    limit: int
    offset: int
    total: int
    permissions: RolePermissionsResponse


@dataclass(frozen=True, slots=True)
class PermissionListResponse:
    data: tuple[PermissionResponse, ...]


@dataclass(frozen=True, slots=True)
class ListRolesRequest:
    limit: int = 20
    offset: int = 0
    search: str | None = None
    kind: str | None = None
    status: str | None = None


@dataclass(frozen=True, slots=True)
class CreateRoleRequest:
    name: str
    description: str | None = None
    permission_ids: tuple[str, ...] = ()
    audit_context: AuditContext | None = None


@dataclass(frozen=True, slots=True)
class GetRoleRequest:
    role_id: str
    audit_context: AuditContext | None = None


@dataclass(frozen=True, slots=True)
class UpdateRoleRequest:
    role_id: str
    name: str
    description: str | None = None
    permission_ids: tuple[str, ...] = ()
    audit_context: AuditContext | None = None


@dataclass(frozen=True, slots=True)
class ListActorRolesRequest:
    actor_id: str
    identity_type: str = "user"


@dataclass(frozen=True, slots=True)
class AssignActorRoleRequest:
    actor_id: str
    role_id: str
    identity_type: str = "user"
    audit_context: AuditContext | None = None


@dataclass(frozen=True, slots=True)
class RevokeActorRoleRequest:
    actor_id: str
    role_id: str
    identity_type: str = "user"
    audit_context: AuditContext | None = None


@dataclass(frozen=True, slots=True)
class UserRoleResponse:
    id: str
    actor_id: str
    role_id: str
    role_name: str
    scope_type: str
    scope_id: str | None
    status: str
    assigned_at: str
    assigned_by: str | None = None


@dataclass(frozen=True, slots=True)
class UserRoleListResponse:
    actor_id: str
    data: tuple[UserRoleResponse, ...]
    permissions: RolePermissionsResponse

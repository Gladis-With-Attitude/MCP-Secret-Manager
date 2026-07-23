from __future__ import annotations

from dataclasses import dataclass

from domain.rbac.permissions import DEFAULT_PERMISSIONS


@dataclass(frozen=True, slots=True)
class RoleDefinition:
    name: str
    description: str
    permissions: tuple[str, ...]


READ_PERMISSIONS = tuple(
    permission
    for permission, _description in DEFAULT_PERMISSIONS
    if permission.endswith(".read") or permission == "role.read"
)

USER_PERMISSIONS = tuple(
    permission
    for permission, _description in DEFAULT_PERMISSIONS
    if permission
    in {
        "vault.create",
        "vault.read",
        "vault.update",
        "project.create",
        "project.read",
        "project.update",
        "project.archive",
        "secret.create",
        "secret.read",
        "secret.update",
        "secret.rotate",
        "apikey.create",
        "apikey.read",
        "apikey.update",
        "apikey.revoke",
        "role.read",
    }
)

DEFAULT_ROLES: tuple[RoleDefinition, ...] = (
    RoleDefinition(
        name="administrator",
        description="System administrator role with all default permissions.",
        permissions=tuple(permission for permission, _description in DEFAULT_PERMISSIONS),
    ),
    RoleDefinition(
        name="user",
        description="Default operator role for day-to-day secret management.",
        permissions=USER_PERMISSIONS,
    ),
    RoleDefinition(
        name="readonly",
        description="Read-only role for metadata and audit consultation.",
        permissions=READ_PERMISSIONS,
    ),
)

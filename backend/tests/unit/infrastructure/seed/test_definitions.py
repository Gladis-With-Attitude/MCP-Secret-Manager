from __future__ import annotations

from domain.rbac.permissions import DEFAULT_PERMISSIONS
from infrastructure.seed.definitions import DEFAULT_ROLES


def test_default_role_permission_matrix_keeps_role_mutations_admin_only() -> None:
    permissions_by_role = {
        role_definition.name: set(role_definition.permissions) for role_definition in DEFAULT_ROLES
    }
    all_default_permissions = {permission for permission, _description in DEFAULT_PERMISSIONS}

    assert permissions_by_role["administrator"] == all_default_permissions
    assert {"role.create", "role.update", "role.assign", "role.revoke"}.isdisjoint(
        permissions_by_role["user"]
    )
    assert permissions_by_role["readonly"] == {
        permission
        for permission in all_default_permissions
        if permission.endswith(".read") or permission == "role.read"
    }

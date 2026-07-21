from __future__ import annotations

from uuid import UUID

import pytest

from domain.identity.value_objects import ApiKeyOwnerType, UserId
from domain.rbac.entities import Permission, Role, RoleAssignment
from domain.rbac.exceptions import RbacValueError
from domain.rbac.value_objects import PermissionName, RoleName, ScopeType


def test_permission_equality_is_based_on_id() -> None:
    permission = Permission.create(PermissionName("secret.read"), "Read secrets.")
    same_permission = Permission(
        id=permission.id,
        name=PermissionName("secret.decrypt"),
        description="Decrypt secrets.",
    )

    assert permission == same_permission
    assert hash(permission) == hash(same_permission)


def test_role_equality_is_based_on_id() -> None:
    role = Role.create(RoleName("reader"), "Read-only role.")
    same_role = Role(id=role.id, name=RoleName("admin"), description="Admin role.")

    assert role == same_role
    assert hash(role) == hash(same_role)


def test_role_assignment_global_scope_must_not_have_scope_id() -> None:
    with pytest.raises(RbacValueError):
        RoleAssignment.create(
            identity_id=UserId.new(),
            identity_type=ApiKeyOwnerType.USER,
            scope_type=ScopeType.GLOBAL,
            scope_id=UUID("f65d3750-f12d-4b86-9753-73652ebc121d"),
            role_id=Role.create(RoleName("reader"), None).id,
        )


def test_role_assignment_scoped_scope_requires_scope_id() -> None:
    with pytest.raises(RbacValueError):
        RoleAssignment.create(
            identity_id=UserId.new(),
            identity_type=ApiKeyOwnerType.USER,
            scope_type=ScopeType.PROJECT,
            scope_id=None,
            role_id=Role.create(RoleName("reader"), None).id,
        )


def test_role_assignment_equality_is_based_on_id() -> None:
    role_id = Role.create(RoleName("reader"), None).id
    assignment = RoleAssignment.create(
        identity_id=UserId.new(),
        identity_type=ApiKeyOwnerType.USER,
        scope_type=ScopeType.PROJECT,
        scope_id=UUID("f65d3750-f12d-4b86-9753-73652ebc121d"),
        role_id=role_id,
    )
    same_assignment = RoleAssignment(
        id=assignment.id,
        identity_id=UserId.new(),
        identity_type=ApiKeyOwnerType.USER,
        scope_type=ScopeType.GLOBAL,
        scope_id=None,
        role_id=role_id,
        created_at=assignment.created_at,
    )

    assert assignment == same_assignment
    assert hash(assignment) == hash(same_assignment)

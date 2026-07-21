from __future__ import annotations

from uuid import UUID

import pytest

from domain.rbac.exceptions import RbacValueError
from domain.rbac.value_objects import (
    PermissionId,
    PermissionName,
    RoleAssignmentId,
    RoleId,
    RoleName,
    ScopeType,
)


def test_permission_id_can_be_created_from_string() -> None:
    permission_id = PermissionId.from_string("dd7f9f6f-4efe-4c18-a8fd-6429d68e4918")

    assert permission_id.value == UUID("dd7f9f6f-4efe-4c18-a8fd-6429d68e4918")
    assert str(permission_id) == "dd7f9f6f-4efe-4c18-a8fd-6429d68e4918"


def test_role_id_can_be_created_from_string() -> None:
    role_id = RoleId.from_string("7e8dd774-1f12-4043-8ccf-9d549bcb18b0")

    assert role_id.value == UUID("7e8dd774-1f12-4043-8ccf-9d549bcb18b0")
    assert str(role_id) == "7e8dd774-1f12-4043-8ccf-9d549bcb18b0"


def test_role_assignment_id_can_be_created_from_string() -> None:
    role_assignment_id = RoleAssignmentId.from_string("1458e91d-9f70-4b44-a736-e07761364929")

    assert role_assignment_id.value == UUID("1458e91d-9f70-4b44-a736-e07761364929")
    assert str(role_assignment_id) == "1458e91d-9f70-4b44-a736-e07761364929"


def test_permission_name_is_trimmed_and_lowercased() -> None:
    permission_name = PermissionName(" Secret.Read ")

    assert permission_name.value == "secret.read"
    assert str(permission_name) == "secret.read"


def test_permission_name_rejects_invalid_format() -> None:
    with pytest.raises(RbacValueError):
        PermissionName("secret read")


def test_permission_name_rejects_too_long_value() -> None:
    with pytest.raises(RbacValueError):
        PermissionName("a" * 121)


def test_role_name_is_trimmed_and_lowercased() -> None:
    role_name = RoleName(" Project-Admin ")

    assert role_name.value == "project-admin"
    assert str(role_name) == "project-admin"


def test_role_name_rejects_invalid_format() -> None:
    with pytest.raises(RbacValueError):
        RoleName("Project Admin")


def test_role_name_rejects_too_long_value() -> None:
    with pytest.raises(RbacValueError):
        RoleName("a" * 101)


def test_scope_type_supports_future_secret_scope() -> None:
    assert ScopeType("secret") is ScopeType.SECRET_RESOURCE

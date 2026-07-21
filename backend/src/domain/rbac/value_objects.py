from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from re import fullmatch
from uuid import UUID, uuid4

from domain.rbac.exceptions import RbacValueError

NAME_PATTERN = r"^[a-z][a-z0-9_.:-]*$"


class ScopeType(StrEnum):
    GLOBAL = "global"
    VAULT = "vault"
    PROJECT = "project"
    SECRET_RESOURCE = "secret"  # noqa: S105 - RBAC scope name, not a secret value.


@dataclass(frozen=True, slots=True)
class PermissionId:
    value: UUID

    @classmethod
    def new(cls) -> PermissionId:
        return cls(uuid4())

    @classmethod
    def from_string(cls, value: str) -> PermissionId:
        return cls(UUID(value))

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class RoleId:
    value: UUID

    @classmethod
    def new(cls) -> RoleId:
        return cls(uuid4())

    @classmethod
    def from_string(cls, value: str) -> RoleId:
        return cls(UUID(value))

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class RoleAssignmentId:
    value: UUID

    @classmethod
    def new(cls) -> RoleAssignmentId:
        return cls(uuid4())

    @classmethod
    def from_string(cls, value: str) -> RoleAssignmentId:
        return cls(UUID(value))

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class PermissionName:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if normalized == "":
            msg = "Permission name is required."
            raise RbacValueError(msg)
        if len(normalized) > 120:
            msg = "Permission name must be at most 120 characters."
            raise RbacValueError(msg)
        if fullmatch(NAME_PATTERN, normalized) is None:
            msg = "Permission name format is invalid."
            raise RbacValueError(msg)
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class RoleName:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if normalized == "":
            msg = "Role name is required."
            raise RbacValueError(msg)
        if len(normalized) > 100:
            msg = "Role name must be at most 100 characters."
            raise RbacValueError(msg)
        if fullmatch(NAME_PATTERN, normalized) is None:
            msg = "Role name format is invalid."
            raise RbacValueError(msg)
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value

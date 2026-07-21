from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from re import fullmatch
from uuid import UUID, uuid4

from domain.audit.exceptions import AuditValueError

AUDIT_NAME_PATTERN = r"^[a-z][a-z0-9_.:-]*$"


class AuditResult(StrEnum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


@dataclass(frozen=True, slots=True)
class AuditEventId:
    value: UUID

    @classmethod
    def new(cls) -> AuditEventId:
        return cls(uuid4())

    @classmethod
    def from_string(cls, value: str) -> AuditEventId:
        return cls(UUID(value))

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class AuditAction:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if normalized == "":
            msg = "Audit action is required."
            raise AuditValueError(msg)
        if len(normalized) > 120:
            msg = "Audit action must be at most 120 characters."
            raise AuditValueError(msg)
        if fullmatch(AUDIT_NAME_PATTERN, normalized) is None:
            msg = "Audit action format is invalid."
            raise AuditValueError(msg)
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class AuditActorType:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if normalized == "":
            msg = "Audit actor type is required."
            raise AuditValueError(msg)
        if len(normalized) > 32:
            msg = "Audit actor type must be at most 32 characters."
            raise AuditValueError(msg)
        if fullmatch(AUDIT_NAME_PATTERN, normalized) is None:
            msg = "Audit actor type format is invalid."
            raise AuditValueError(msg)
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class AuditResourceType:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if normalized == "":
            msg = "Audit resource type is required."
            raise AuditValueError(msg)
        if len(normalized) > 64:
            msg = "Audit resource type must be at most 64 characters."
            raise AuditValueError(msg)
        if fullmatch(AUDIT_NAME_PATTERN, normalized) is None:
            msg = "Audit resource type format is invalid."
            raise AuditValueError(msg)
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value

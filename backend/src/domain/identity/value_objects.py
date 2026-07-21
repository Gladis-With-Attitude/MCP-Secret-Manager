from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from re import fullmatch
from uuid import UUID, uuid4

from domain.identity.exceptions import IdentityValueError

EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class IdentityStatus(StrEnum):
    ACTIVE = "active"
    DISABLED = "disabled"


class ApiKeyOwnerType(StrEnum):
    USER = "user"
    SERVICE_ACCOUNT = "service_account"


@dataclass(frozen=True, slots=True)
class UserId:
    value: UUID

    @classmethod
    def new(cls) -> UserId:
        return cls(uuid4())

    @classmethod
    def from_string(cls, value: str) -> UserId:
        return cls(UUID(value))

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class ServiceAccountId:
    value: UUID

    @classmethod
    def new(cls) -> ServiceAccountId:
        return cls(uuid4())

    @classmethod
    def from_string(cls, value: str) -> ServiceAccountId:
        return cls(UUID(value))

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class ApiKeyId:
    value: UUID

    @classmethod
    def new(cls) -> ApiKeyId:
        return cls(uuid4())

    @classmethod
    def from_string(cls, value: str) -> ApiKeyId:
        return cls(UUID(value))

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class UserEmail:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if normalized == "":
            msg = "User email is required."
            raise IdentityValueError(msg)
        if len(normalized) > 254:
            msg = "User email must be at most 254 characters."
            raise IdentityValueError(msg)
        if fullmatch(EMAIL_PATTERN, normalized) is None:
            msg = "User email must be valid."
            raise IdentityValueError(msg)
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class UserDisplayName:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if normalized == "":
            msg = "User display name is required."
            raise IdentityValueError(msg)
        if len(normalized) > 100:
            msg = "User display name must be at most 100 characters."
            raise IdentityValueError(msg)
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ServiceAccountName:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        if normalized == "":
            msg = "Service account name is required."
            raise IdentityValueError(msg)
        if len(normalized) < 3 or len(normalized) > 100:
            msg = "Service account name must be between 3 and 100 characters."
            raise IdentityValueError(msg)
        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value

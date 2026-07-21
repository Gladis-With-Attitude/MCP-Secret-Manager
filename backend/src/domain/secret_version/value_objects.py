from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4

from domain.secret_version.exceptions import SecretValueError, SecretVersionNumberError


@dataclass(frozen=True, slots=True)
class SecretVersionId:
    value: UUID

    @classmethod
    def new(cls) -> SecretVersionId:
        return cls(value=uuid4())

    @classmethod
    def from_string(cls, value: str) -> SecretVersionId:
        return cls(value=UUID(value))

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class SecretValue:
    value: str

    def __post_init__(self) -> None:
        if self.value == "":
            msg = "Secret value is required."
            raise SecretValueError(msg)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class SecretVersionNumber:
    value: int

    def __post_init__(self) -> None:
        if self.value < 1:
            msg = "Secret version number must be greater than or equal to 1."
            raise SecretVersionNumberError(msg)

    def __int__(self) -> int:
        return self.value

from __future__ import annotations

import re
from dataclasses import dataclass
from uuid import UUID, uuid4

from domain.secret.exceptions import SecretKeyError

SECRET_KEY_PATTERN = re.compile(r"^[A-Z0-9_]+$")


@dataclass(frozen=True, slots=True)
class SecretId:
    value: UUID

    @classmethod
    def new(cls) -> SecretId:
        return cls(value=uuid4())

    @classmethod
    def from_string(cls, value: str) -> SecretId:
        return cls(value=UUID(value))

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class SecretKey:
    value: str

    MIN_LENGTH = 3
    MAX_LENGTH = 128

    def __post_init__(self) -> None:
        length = len(self.value)

        if length == 0:
            msg = "Secret key is required."
            raise SecretKeyError(msg)

        if length < self.MIN_LENGTH:
            msg = f"Secret key must contain at least {self.MIN_LENGTH} characters."
            raise SecretKeyError(msg)

        if length > self.MAX_LENGTH:
            msg = f"Secret key must contain at most {self.MAX_LENGTH} characters."
            raise SecretKeyError(msg)

        if SECRET_KEY_PATTERN.fullmatch(self.value) is None:
            msg = "Secret key must contain only A-Z, 0-9 and underscore characters."
            raise SecretKeyError(msg)

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class SecretDescription:
    value: str | None

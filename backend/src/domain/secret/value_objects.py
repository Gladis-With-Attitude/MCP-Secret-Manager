from __future__ import annotations

import re
from dataclasses import dataclass
from uuid import UUID, uuid4

from domain.secret.exceptions import (
    SecretDescriptionError,
    SecretKeyError,
    SecretMetadataError,
    SecretTagError,
    SecretTypeError,
)

SECRET_KEY_PATTERN = re.compile(r"^[A-Z0-9_]+$")
SECRET_TAG_PATTERN = re.compile(r"^[a-zA-Z0-9_.:-]+$")
SECRET_TYPES = frozenset({"api_key", "certificate", "generic", "password", "token", "other"})
SecretMetadataValue = bool | int | float | str
SecretMetadata = dict[str, SecretMetadataValue]


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

    MAX_LENGTH = 280

    def __post_init__(self) -> None:
        if self.value is None:
            return

        normalized = self.value.strip()
        if not normalized:
            object.__setattr__(self, "value", None)
            return

        if len(normalized) > self.MAX_LENGTH:
            msg = f"Secret description must contain at most {self.MAX_LENGTH} characters."
            raise SecretDescriptionError(msg)

        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class SecretType:
    value: str

    def __post_init__(self) -> None:
        normalized = self.value.strip().lower()
        if normalized not in SECRET_TYPES:
            msg = "Secret type is invalid."
            raise SecretTypeError(msg)
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class SecretTags:
    value: tuple[str, ...]

    MAX_COUNT = 12
    MAX_LENGTH = 40

    def __post_init__(self) -> None:
        normalized: list[str] = []
        seen: set[str] = set()
        for raw_tag in self.value:
            tag = raw_tag.strip()
            if not tag:
                continue
            if len(tag) > self.MAX_LENGTH:
                msg = f"Secret tags must contain at most {self.MAX_LENGTH} characters."
                raise SecretTagError(msg)
            if SECRET_TAG_PATTERN.fullmatch(tag) is None:
                msg = "Secret tags may contain letters, numbers, underscore, dot, colon or dash."
                raise SecretTagError(msg)
            if tag not in seen:
                normalized.append(tag)
                seen.add(tag)

        if len(normalized) > self.MAX_COUNT:
            msg = f"Use at most {self.MAX_COUNT} secret tags."
            raise SecretTagError(msg)

        object.__setattr__(self, "value", tuple(normalized))


@dataclass(frozen=True, slots=True)
class SecretMetadataObject:
    value: SecretMetadata

    MAX_KEYS = 50
    MAX_KEY_LENGTH = 80
    MAX_STRING_VALUE_LENGTH = 500

    def __post_init__(self) -> None:
        if len(self.value) > self.MAX_KEYS:
            msg = f"Secret metadata must contain at most {self.MAX_KEYS} keys."
            raise SecretMetadataError(msg)

        normalized: SecretMetadata = {}
        for raw_key, raw_value in self.value.items():
            key = raw_key.strip()
            if not key:
                msg = "Secret metadata keys must not be empty."
                raise SecretMetadataError(msg)
            if len(key) > self.MAX_KEY_LENGTH:
                msg = f"Secret metadata keys must contain at most {self.MAX_KEY_LENGTH} characters."
                raise SecretMetadataError(msg)
            if isinstance(raw_value, str):
                string_value = raw_value.strip()
                if len(string_value) > self.MAX_STRING_VALUE_LENGTH:
                    msg = (
                        "Secret metadata string values must contain at most "
                        f"{self.MAX_STRING_VALUE_LENGTH} characters."
                    )
                    raise SecretMetadataError(msg)
                value: SecretMetadataValue = string_value
            elif isinstance(raw_value, bool | int | float):
                value = raw_value
            else:
                msg = "Secret metadata values must be strings, numbers or booleans."
                raise SecretMetadataError(msg)
            normalized[key] = value

        object.__setattr__(self, "value", normalized)

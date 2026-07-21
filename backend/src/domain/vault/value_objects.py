from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4

from domain.vault.exceptions import VaultNameError


@dataclass(frozen=True, slots=True)
class VaultId:
    value: UUID

    @classmethod
    def new(cls) -> VaultId:
        return cls(value=uuid4())

    @classmethod
    def from_string(cls, value: str) -> VaultId:
        return cls(value=UUID(value))

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True, slots=True)
class VaultName:
    value: str

    MIN_LENGTH = 3
    MAX_LENGTH = 100

    def __post_init__(self) -> None:
        normalized = self.value.strip()
        length = len(normalized)

        if length == 0:
            msg = "Vault name is required."
            raise VaultNameError(msg)

        if length < self.MIN_LENGTH:
            msg = f"Vault name must contain at least {self.MIN_LENGTH} characters."
            raise VaultNameError(msg)

        if length > self.MAX_LENGTH:
            msg = f"Vault name must contain at most {self.MAX_LENGTH} characters."
            raise VaultNameError(msg)

        object.__setattr__(self, "value", normalized)

    def __str__(self) -> str:
        return self.value

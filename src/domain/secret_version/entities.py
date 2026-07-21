from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import UTC, datetime

from domain.secret.value_objects import SecretId
from domain.secret_version.value_objects import (
    SecretValue,
    SecretVersionId,
    SecretVersionNumber,
)


@dataclass(frozen=True, slots=True, eq=False)
class SecretVersion:
    id: SecretVersionId
    secret_id: SecretId
    value: SecretValue
    version: SecretVersionNumber
    active: bool
    created_at: datetime

    @classmethod
    def create(
        cls,
        secret_id: SecretId,
        value: SecretValue,
        version: SecretVersionNumber,
    ) -> SecretVersion:
        return cls(
            id=SecretVersionId.new(),
            secret_id=secret_id,
            value=value,
            version=version,
            active=True,
            created_at=datetime.now(UTC),
        )

    def deactivate(self) -> SecretVersion:
        return replace(self, active=False)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SecretVersion):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

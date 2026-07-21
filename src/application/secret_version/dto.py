from __future__ import annotations

from dataclasses import dataclass

from domain.secret_version.entities import SecretVersion


@dataclass(frozen=True, slots=True)
class CreateSecretVersionRequest:
    secret_id: str
    value: str


@dataclass(frozen=True, slots=True)
class SecretVersionResponse:
    id: str
    secret_id: str
    value: str
    version: int
    active: bool
    created_at: str

    @classmethod
    def from_domain(cls, secret_version: SecretVersion) -> SecretVersionResponse:
        return cls(
            id=str(secret_version.id),
            secret_id=str(secret_version.secret_id),
            value=secret_version.value.value,
            version=secret_version.version.value,
            active=secret_version.active,
            created_at=secret_version.created_at.isoformat(),
        )

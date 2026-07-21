from __future__ import annotations

from dataclasses import dataclass

from domain.secret.entities import Secret


@dataclass(frozen=True, slots=True)
class CreateSecretRequest:
    project_id: str
    key: str
    description: str | None = None


@dataclass(frozen=True, slots=True)
class SecretResponse:
    id: str
    project_id: str
    key: str
    description: str | None

    @classmethod
    def from_domain(cls, secret: Secret) -> SecretResponse:
        return cls(
            id=str(secret.id),
            project_id=str(secret.project_id),
            key=secret.key.value,
            description=secret.description.value,
        )

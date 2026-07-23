from __future__ import annotations

from dataclasses import dataclass

from application.audit.dto import AuditContext
from domain.secret_version.entities import SecretVersion
from domain.secret_version.value_objects import SecretValue


@dataclass(frozen=True, slots=True)
class CreateSecretVersionRequest:
    secret_id: str
    value: str
    project_id: str | None = None
    audit_context: AuditContext | None = None


@dataclass(frozen=True, slots=True)
class RestoreSecretVersionRequest:
    secret_id: str
    version_id: str
    project_id: str | None = None
    audit_context: AuditContext | None = None


@dataclass(frozen=True, slots=True)
class SecretVersionResponse:
    id: str
    secret_id: str
    value: str
    version: int
    active: bool
    created_at: str

    @classmethod
    def from_domain(
        cls,
        secret_version: SecretVersion,
        decrypted_value: SecretValue,
    ) -> SecretVersionResponse:
        return cls(
            id=str(secret_version.id),
            secret_id=str(secret_version.secret_id),
            value=decrypted_value.value,
            version=secret_version.version.value,
            active=secret_version.active,
            created_at=secret_version.created_at.isoformat(),
        )


@dataclass(frozen=True, slots=True)
class SecretVersionMetadataResponse:
    id: str
    secret_id: str
    version: int
    active: bool
    created_at: str

    @classmethod
    def from_domain(cls, secret_version: SecretVersion) -> SecretVersionMetadataResponse:
        return cls(
            id=str(secret_version.id),
            secret_id=str(secret_version.secret_id),
            version=secret_version.version.value,
            active=secret_version.active,
            created_at=secret_version.created_at.isoformat(),
        )

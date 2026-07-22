from __future__ import annotations

from dataclasses import dataclass

from application.audit.dto import AuditContext
from domain.secret.entities import Secret
from domain.secret.value_objects import SecretMetadata, SecretMetadataValue


@dataclass(frozen=True, slots=True)
class CreateSecretRequest:
    project_id: str
    key: str
    description: str | None = None
    type: str = "generic"
    metadata: SecretMetadata | None = None
    tags: tuple[str, ...] = ()
    audit_context: AuditContext | None = None


@dataclass(frozen=True, slots=True)
class GetSecretRequest:
    secret_id: str
    project_id: str | None = None
    audit_context: AuditContext | None = None


@dataclass(frozen=True, slots=True)
class ListSecretsRequest:
    project_id: str
    page: int = 1
    page_size: int = 20
    search: str | None = None
    status: str | None = None
    archived: bool | None = None
    type: str | None = None
    audit_context: AuditContext | None = None


@dataclass(frozen=True, slots=True)
class SearchSecretsRequest:
    project_id: str
    query: str
    audit_context: AuditContext | None = None


@dataclass(frozen=True, slots=True)
class UpdateSecretRequest:
    secret_id: str
    key: str
    description: str | None = None
    type: str = "generic"
    metadata: SecretMetadata | None = None
    tags: tuple[str, ...] = ()
    audit_context: AuditContext | None = None


@dataclass(frozen=True, slots=True)
class ArchiveSecretRequest:
    secret_id: str
    audit_context: AuditContext | None = None


@dataclass(frozen=True, slots=True)
class SecretResponse:
    id: str
    project_id: str
    key: str
    description: str | None
    type: str = "generic"
    metadata: dict[str, SecretMetadataValue] | None = None
    tags: tuple[str, ...] = ()
    archived: bool = False
    status: str = "active"
    created_at: str = ""
    updated_at: str = ""
    archived_at: str | None = None

    @classmethod
    def from_domain(cls, secret: Secret) -> SecretResponse:
        status = "archived" if secret.archived else "active"
        return cls(
            id=str(secret.id),
            project_id=str(secret.project_id),
            key=secret.key.value,
            description=secret.description.value,
            type=secret.type.value,
            metadata=secret.metadata.value,
            tags=secret.tags.value,
            archived=secret.archived,
            status=status,
            created_at=secret.created_at.isoformat(),
            updated_at=secret.updated_at.isoformat(),
            archived_at=secret.archived_at.isoformat() if secret.archived_at else None,
        )


@dataclass(frozen=True, slots=True)
class SecretPermissionsResponse:
    create: bool
    read: bool
    update: bool
    archive: bool
    delete: bool
    read_value: bool


@dataclass(frozen=True, slots=True)
class PaginationResponse:
    page: int
    page_size: int
    total: int
    has_next_page: bool
    has_previous_page: bool


@dataclass(frozen=True, slots=True)
class SecretListResponse:
    data: tuple[SecretResponse, ...]
    pagination: PaginationResponse
    permissions: SecretPermissionsResponse

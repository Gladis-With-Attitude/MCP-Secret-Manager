from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from application.audit.dto import AuditContext
from domain.identity.entities import ApiKey, ServiceAccount, User


@dataclass(frozen=True, slots=True)
class CreateUserRequest:
    email: str
    display_name: str
    audit_context: AuditContext | None = None


@dataclass(frozen=True, slots=True)
class UserResponse:
    id: str
    email: str
    display_name: str
    status: str
    created_at: str

    @classmethod
    def from_domain(cls, user: User) -> UserResponse:
        return cls(
            id=str(user.id),
            email=user.email.value,
            display_name=user.display_name.value,
            status=user.status.value,
            created_at=user.created_at.isoformat(),
        )


@dataclass(frozen=True, slots=True)
class CreateServiceAccountRequest:
    project_id: str
    name: str
    description: str | None
    audit_context: AuditContext | None = None


@dataclass(frozen=True, slots=True)
class ServiceAccountResponse:
    id: str
    project_id: str
    name: str
    description: str | None
    status: str
    created_at: str

    @classmethod
    def from_domain(cls, service_account: ServiceAccount) -> ServiceAccountResponse:
        return cls(
            id=str(service_account.id),
            project_id=str(service_account.project_id),
            name=service_account.name.value,
            description=service_account.description,
            status=service_account.status.value,
            created_at=service_account.created_at.isoformat(),
        )


@dataclass(frozen=True, slots=True)
class CreateApiKeyRequest:
    owner_id: str
    owner_type: str
    expires_at: str | None
    name: str | None = None
    description: str | None = None
    granted_permissions: tuple[str, ...] = ()
    scopes: tuple[str, ...] = ()
    audit_context: AuditContext | None = None


@dataclass(frozen=True, slots=True)
class ApiKeyResponse:
    id: str
    name: str
    description: str | None
    key_prefix: str
    owner_id: str
    owner_type: str
    granted_permissions: tuple[str, ...]
    scopes: tuple[str, ...]
    status: str
    expires_at: str | None
    revoked_at: str | None
    created_at: str
    last_used_at: str | None = None
    owner_name: str | None = None

    @classmethod
    def from_domain(cls, api_key: ApiKey) -> ApiKeyResponse:
        status = "revoked"
        if api_key.revoked_at is None:
            status = "expired" if api_key.is_expired(datetime.now(UTC)) else "active"
        return cls(
            id=str(api_key.id),
            name=api_key.name or api_key.key_prefix,
            description=api_key.description,
            key_prefix=api_key.key_prefix,
            owner_id=str(api_key.owner_id),
            owner_type=api_key.owner_type.value,
            granted_permissions=api_key.granted_permissions,
            scopes=api_key.scopes,
            status=status,
            expires_at=api_key.expires_at.isoformat() if api_key.expires_at is not None else None,
            revoked_at=api_key.revoked_at.isoformat() if api_key.revoked_at is not None else None,
            created_at=api_key.created_at.isoformat(),
        )


@dataclass(frozen=True, slots=True)
class ApiKeyCreatedResponse:
    id: str
    api_key: str
    name: str
    description: str | None
    key_prefix: str
    owner_id: str
    owner_type: str
    granted_permissions: tuple[str, ...]
    scopes: tuple[str, ...]
    status: str
    expires_at: str | None
    revoked_at: str | None
    created_at: str
    last_used_at: str | None = None
    owner_name: str | None = None

    @classmethod
    def from_domain(cls, api_key: ApiKey, raw_api_key: str) -> ApiKeyCreatedResponse:
        metadata = ApiKeyResponse.from_domain(api_key)
        return cls(
            id=metadata.id,
            name=metadata.name,
            description=metadata.description,
            key_prefix=metadata.key_prefix,
            owner_id=metadata.owner_id,
            owner_type=metadata.owner_type,
            granted_permissions=metadata.granted_permissions,
            scopes=metadata.scopes,
            status=metadata.status,
            expires_at=metadata.expires_at,
            revoked_at=metadata.revoked_at,
            created_at=metadata.created_at,
            last_used_at=metadata.last_used_at,
            owner_name=metadata.owner_name,
            api_key=raw_api_key,
        )


@dataclass(frozen=True, slots=True)
class ApiKeyPermissionsResponse:
    create: bool
    read: bool
    revoke: bool
    update: bool


@dataclass(frozen=True, slots=True)
class ApiKeyPaginationResponse:
    page: int
    page_size: int
    total: int
    has_next_page: bool
    has_previous_page: bool


@dataclass(frozen=True, slots=True)
class ListApiKeysRequest:
    page: int = 1
    page_size: int = 20
    search: str | None = None
    status: str | None = None


@dataclass(frozen=True, slots=True)
class GetApiKeyRequest:
    api_key_id: str
    audit_context: AuditContext | None = None


@dataclass(frozen=True, slots=True)
class RevokeApiKeyRequest:
    api_key_id: str
    audit_context: AuditContext | None = None


@dataclass(frozen=True, slots=True)
class UpdateApiKeyRequest:
    api_key_id: str
    name: str | None
    description: str | None
    expires_at: str | None
    granted_permissions: tuple[str, ...] = ()
    scopes: tuple[str, ...] = ()
    audit_context: AuditContext | None = None


@dataclass(frozen=True, slots=True)
class ApiKeyListResponse:
    data: tuple[ApiKeyResponse, ...]
    pagination: ApiKeyPaginationResponse
    permissions: ApiKeyPermissionsResponse


@dataclass(frozen=True, slots=True)
class AuthenticatedIdentityResponse:
    id: str
    type: str
    api_key_id: str
    session_id: str | None = None


@dataclass(frozen=True, slots=True)
class CreateSessionRequest:
    api_key: str
    audit_context: AuditContext | None = None


@dataclass(frozen=True, slots=True)
class SessionCreatedResponse:
    session_token: str
    session: CurrentSessionResponse


@dataclass(frozen=True, slots=True)
class CurrentSessionResponse:
    api_key_id: str
    auth_method: str
    expires_at: str | None
    issued_at: str
    user_id: str
    user_type: str
    email: str | None
    name: str
    profile_label: str

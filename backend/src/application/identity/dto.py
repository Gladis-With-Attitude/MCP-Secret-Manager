from __future__ import annotations

from dataclasses import dataclass

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
    audit_context: AuditContext | None = None


@dataclass(frozen=True, slots=True)
class ApiKeyCreatedResponse:
    id: str
    api_key: str
    key_prefix: str
    owner_id: str
    owner_type: str
    expires_at: str | None
    created_at: str

    @classmethod
    def from_domain(cls, api_key: ApiKey, raw_api_key: str) -> ApiKeyCreatedResponse:
        return cls(
            id=str(api_key.id),
            api_key=raw_api_key,
            key_prefix=api_key.key_prefix,
            owner_id=str(api_key.owner_id),
            owner_type=api_key.owner_type.value,
            expires_at=api_key.expires_at.isoformat() if api_key.expires_at is not None else None,
            created_at=api_key.created_at.isoformat(),
        )


@dataclass(frozen=True, slots=True)
class AuthenticatedIdentityResponse:
    id: str
    type: str
    api_key_id: str

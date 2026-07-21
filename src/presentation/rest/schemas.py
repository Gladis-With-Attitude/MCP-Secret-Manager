from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from application.audit.dto import AuditEventResponse
from application.identity.dto import (
    ApiKeyCreatedResponse,
    ServiceAccountResponse,
    UserResponse,
)
from application.project.dto import ProjectResponse
from application.secret.dto import SecretResponse
from application.secret_version.dto import SecretVersionResponse
from application.vault.dto import VaultResponse
from domain.audit.entities import AuditMetadata


class CreateVaultHttpRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str


class VaultHttpResponse(BaseModel):
    id: str
    name: str

    @classmethod
    def from_application(cls, response: VaultResponse) -> VaultHttpResponse:
        return cls(id=response.id, name=response.name)


class CreateProjectHttpRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str


class ProjectHttpResponse(BaseModel):
    id: str
    vault_id: str
    name: str

    @classmethod
    def from_application(cls, response: ProjectResponse) -> ProjectHttpResponse:
        return cls(id=response.id, vault_id=response.vault_id, name=response.name)


class CreateSecretHttpRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str
    description: str | None = None


class SecretHttpResponse(BaseModel):
    id: str
    project_id: str
    key: str
    description: str | None

    @classmethod
    def from_application(cls, response: SecretResponse) -> SecretHttpResponse:
        return cls(
            id=response.id,
            project_id=response.project_id,
            key=response.key,
            description=response.description,
        )


class CreateSecretVersionHttpRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    value: str


class SecretVersionHttpResponse(BaseModel):
    id: str
    secret_id: str
    value: str
    version: int
    active: bool
    created_at: str

    @classmethod
    def from_application(cls, response: SecretVersionResponse) -> SecretVersionHttpResponse:
        return cls(
            id=response.id,
            secret_id=response.secret_id,
            value=response.value,
            version=response.version,
            active=response.active,
            created_at=response.created_at,
        )


class CreateUserHttpRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str
    display_name: str


class UserHttpResponse(BaseModel):
    id: str
    email: str
    display_name: str
    status: str
    created_at: str

    @classmethod
    def from_application(cls, response: UserResponse) -> UserHttpResponse:
        return cls(
            id=response.id,
            email=response.email,
            display_name=response.display_name,
            status=response.status,
            created_at=response.created_at,
        )


class CreateServiceAccountHttpRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    project_id: str
    name: str
    description: str | None = None


class ServiceAccountHttpResponse(BaseModel):
    id: str
    project_id: str
    name: str
    description: str | None
    status: str
    created_at: str

    @classmethod
    def from_application(cls, response: ServiceAccountResponse) -> ServiceAccountHttpResponse:
        return cls(
            id=response.id,
            project_id=response.project_id,
            name=response.name,
            description=response.description,
            status=response.status,
            created_at=response.created_at,
        )


class CreateApiKeyHttpRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    owner_id: str
    owner_type: str
    expires_at: str | None = None


class ApiKeyCreatedHttpResponse(BaseModel):
    id: str
    api_key: str
    key_prefix: str
    owner_id: str
    owner_type: str
    expires_at: str | None
    created_at: str

    @classmethod
    def from_application(cls, response: ApiKeyCreatedResponse) -> ApiKeyCreatedHttpResponse:
        return cls(
            id=response.id,
            api_key=response.api_key,
            key_prefix=response.key_prefix,
            owner_id=response.owner_id,
            owner_type=response.owner_type,
            expires_at=response.expires_at,
            created_at=response.created_at,
        )


class AuditEventHttpResponse(BaseModel):
    id: str
    timestamp: str
    actor_id: str | None
    actor_type: str
    action: str
    resource_type: str
    resource_id: str | None
    result: str
    ip_address: str | None
    user_agent: str | None
    request_id: str | None
    metadata: AuditMetadata

    @classmethod
    def from_application(cls, response: AuditEventResponse) -> AuditEventHttpResponse:
        return cls(
            id=response.id,
            timestamp=response.timestamp,
            actor_id=response.actor_id,
            actor_type=response.actor_type,
            action=response.action,
            resource_type=response.resource_type,
            resource_id=response.resource_id,
            result=response.result,
            ip_address=response.ip_address,
            user_agent=response.user_agent,
            request_id=response.request_id,
            metadata=response.metadata,
        )

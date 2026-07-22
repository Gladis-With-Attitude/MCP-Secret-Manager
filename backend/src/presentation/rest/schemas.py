from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from application.audit.dto import AuditEventResponse
from application.identity.dto import (
    ApiKeyCreatedResponse,
    ServiceAccountResponse,
    UserResponse,
)
from application.project.dto import ProjectListResponse, ProjectResponse
from application.secret.dto import SecretResponse
from application.secret_version.dto import SecretVersionResponse
from application.vault.dto import VaultListResponse, VaultResponse
from domain.audit.entities import AuditMetadata


class CreateVaultHttpRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str | None = None
    name: str


class UpdateVaultHttpRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str | None = None
    name: str


class VaultPermissionHttpResponse(BaseModel):
    archive: bool
    create: bool
    lock: bool
    read: bool
    update: bool


class VaultHttpResponse(BaseModel):
    archived: bool
    archived_at: str | None
    created_at: str
    description: str | None
    id: str
    locked: bool
    name: str
    permissions: VaultPermissionHttpResponse | None = None
    status: str
    updated_at: str

    @classmethod
    def from_application(
        cls,
        response: VaultResponse,
        permissions: VaultPermissionHttpResponse | None = None,
    ) -> VaultHttpResponse:
        return cls(
            archived=response.archived,
            archived_at=response.archived_at,
            created_at=response.created_at,
            description=response.description,
            id=response.id,
            locked=response.locked,
            name=response.name,
            permissions=permissions,
            status=response.status,
            updated_at=response.updated_at,
        )


class PaginationHttpResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    has_next_page: bool = Field(alias="hasNextPage")
    has_previous_page: bool = Field(alias="hasPreviousPage")
    page: int
    page_size: int = Field(alias="pageSize")
    total: int


class VaultListHttpResponse(BaseModel):
    data: list[VaultHttpResponse]
    pagination: PaginationHttpResponse
    permissions: VaultPermissionHttpResponse
    success: bool = True

    @classmethod
    def from_application(cls, response: VaultListResponse) -> VaultListHttpResponse:
        permissions = VaultPermissionHttpResponse(
            archive=response.permissions.archive,
            create=response.permissions.create,
            lock=response.permissions.lock,
            read=response.permissions.read,
            update=response.permissions.update,
        )
        return cls(
            data=[
                VaultHttpResponse.from_application(item, permissions=permissions)
                for item in response.data
            ],
            pagination=PaginationHttpResponse(
                hasNextPage=response.pagination.has_next_page,
                hasPreviousPage=response.pagination.has_previous_page,
                page=response.pagination.page,
                pageSize=response.pagination.page_size,
                total=response.pagination.total,
            ),
            permissions=permissions,
        )


class CreateProjectHttpRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str | None = None
    name: str


class UpdateProjectHttpRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str | None = None
    name: str


class ProjectPermissionHttpResponse(BaseModel):
    archive: bool
    create: bool
    delete: bool
    read: bool
    update: bool


class ProjectHttpResponse(BaseModel):
    archived: bool
    archived_at: str | None
    created_at: str
    description: str | None
    id: str
    name: str
    permissions: ProjectPermissionHttpResponse | None = None
    status: str
    updated_at: str
    vault_id: str

    @classmethod
    def from_application(
        cls,
        response: ProjectResponse,
        permissions: ProjectPermissionHttpResponse | None = None,
    ) -> ProjectHttpResponse:
        return cls(
            archived=response.archived,
            archived_at=response.archived_at,
            created_at=response.created_at,
            description=response.description,
            id=response.id,
            name=response.name,
            permissions=permissions,
            status=response.status,
            updated_at=response.updated_at,
            vault_id=response.vault_id,
        )


class ProjectListHttpResponse(BaseModel):
    data: list[ProjectHttpResponse]
    pagination: PaginationHttpResponse
    permissions: ProjectPermissionHttpResponse
    success: bool = True

    @classmethod
    def from_application(cls, response: ProjectListResponse) -> ProjectListHttpResponse:
        permissions = ProjectPermissionHttpResponse(
            archive=response.permissions.archive,
            create=response.permissions.create,
            delete=response.permissions.delete,
            read=response.permissions.read,
            update=response.permissions.update,
        )
        return cls(
            data=[
                ProjectHttpResponse.from_application(item, permissions=permissions)
                for item in response.data
            ],
            pagination=PaginationHttpResponse(
                hasNextPage=response.pagination.has_next_page,
                hasPreviousPage=response.pagination.has_previous_page,
                page=response.pagination.page,
                pageSize=response.pagination.page_size,
                total=response.pagination.total,
            ),
            permissions=permissions,
        )


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

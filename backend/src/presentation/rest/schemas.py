from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from application.audit.dto import AuditEventResponse
from application.identity.dto import (
    AccountSecurityResponse,
    ActiveSessionListResponse,
    ActiveSessionResponse,
    ApiKeyCreatedResponse,
    ApiKeyListResponse,
    ApiKeyPermissionsResponse,
    ApiKeyResponse,
    CurrentSessionResponse,
    NotificationPreferencesResponse,
    ProfilePermissionsResponse,
    PublicSettingsResponse,
    ServiceAccountResponse,
    SettingsPermissionsResponse,
    SettingsResponse,
    UserPreferencesResponse,
    UserProfileResponse,
    UserResponse,
)
from application.project.dto import ProjectListResponse, ProjectResponse
from application.rbac.dto import (
    PermissionListResponse,
    PermissionResponse,
    RoleListResponse,
    RolePermissionsResponse,
    RoleResponse,
    UserRoleListResponse,
    UserRoleResponse,
)
from application.secret.dto import SecretListResponse, SecretResponse
from application.secret_version.dto import SecretVersionMetadataResponse, SecretVersionResponse
from application.vault.dto import VaultListResponse, VaultResponse
from domain.audit.entities import AuditMetadata
from domain.secret.value_objects import SecretMetadata, SecretMetadataValue


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
    type: str = "generic"
    metadata: SecretMetadata = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)


class UpdateSecretHttpRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str
    description: str | None = None
    type: str = "generic"
    metadata: SecretMetadata = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)


class SecretPermissionHttpResponse(BaseModel):
    archive: bool
    create: bool
    delete: bool
    read: bool
    read_value: bool
    update: bool


class SecretHttpResponse(BaseModel):
    archived: bool
    archived_at: str | None
    created_at: str
    current_version: int | None = None
    description: str | None
    id: str
    key: str
    last_version_at: str | None = None
    metadata: dict[str, SecretMetadataValue]
    name: str
    permissions: SecretPermissionHttpResponse | None = None
    project_id: str
    provider: str = "local"
    status: str
    tags: list[str]
    type: str
    updated_at: str
    version_count: int | None = None

    @classmethod
    def from_application(
        cls,
        response: SecretResponse,
        permissions: SecretPermissionHttpResponse | None = None,
    ) -> SecretHttpResponse:
        return cls(
            archived=response.archived,
            archived_at=response.archived_at,
            created_at=response.created_at,
            description=response.description,
            id=response.id,
            key=response.key,
            metadata=response.metadata or {},
            name=response.key,
            permissions=permissions,
            project_id=response.project_id,
            status=response.status,
            tags=list(response.tags),
            type=response.type,
            updated_at=response.updated_at,
        )


class SecretListHttpResponse(BaseModel):
    data: list[SecretHttpResponse]
    pagination: PaginationHttpResponse
    permissions: SecretPermissionHttpResponse
    success: bool = True

    @classmethod
    def from_application(cls, response: SecretListResponse) -> SecretListHttpResponse:
        permissions = SecretPermissionHttpResponse(
            archive=response.permissions.archive,
            create=response.permissions.create,
            delete=response.permissions.delete,
            read=response.permissions.read,
            read_value=response.permissions.read_value,
            update=response.permissions.update,
        )
        return cls(
            data=[
                SecretHttpResponse.from_application(item, permissions=permissions)
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


class CreateSecretVersionHttpRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    make_current: bool = True
    metadata: SecretMetadata = Field(default_factory=dict)
    note: str | None = None
    value: str


class SecretVersionValueHttpResponse(BaseModel):
    id: str
    secret_id: str
    value: str
    version: int
    active: bool
    created_at: str

    @classmethod
    def from_application(cls, response: SecretVersionResponse) -> SecretVersionValueHttpResponse:
        return cls(
            id=response.id,
            secret_id=response.secret_id,
            value=response.value,
            version=response.version,
            active=response.active,
            created_at=response.created_at,
        )


class SecretVersionMetadataHttpResponse(BaseModel):
    id: str
    secret_id: str
    version: int
    active: bool
    created_at: str

    @classmethod
    def from_application(
        cls,
        response: SecretVersionMetadataResponse,
    ) -> SecretVersionMetadataHttpResponse:
        return cls(
            id=response.id,
            secret_id=response.secret_id,
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

    description: str | None = None
    owner_id: str
    owner_type: str
    name: str | None = None
    permissions: list[str] = Field(default_factory=list)
    scopes: list[str] = Field(default_factory=list)
    expires_at: str | None = None


class UpdateApiKeyHttpRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str | None = None
    expires_at: str | None = None
    name: str | None = None
    permissions: list[str] = Field(default_factory=list)
    scopes: list[str] = Field(default_factory=list)


class CreateSessionHttpRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_key: str


class ApiKeyPermissionHttpResponse(BaseModel):
    create: bool
    read: bool
    revoke: bool
    update: bool

    @classmethod
    def from_application(
        cls,
        response: ApiKeyPermissionsResponse,
    ) -> ApiKeyPermissionHttpResponse:
        return cls(
            create=response.create,
            read=response.read,
            revoke=response.revoke,
            update=response.update,
        )


class ApiKeyHttpResponse(BaseModel):
    id: str
    name: str
    description: str | None
    key_prefix: str
    owner_id: str
    owner_name: str | None = None
    owner_type: str
    granted_permissions: list[str]
    permission_names: list[str]
    roles: list[str]
    scopes: list[str]
    status: str
    permissions: ApiKeyPermissionHttpResponse | None = None
    last_used_at: str | None
    expires_at: str | None
    revoked_at: str | None
    created_at: str

    @classmethod
    def from_application(
        cls,
        response: ApiKeyCreatedResponse | ApiKeyResponse,
        permissions: ApiKeyPermissionHttpResponse | None = None,
    ) -> ApiKeyHttpResponse:
        return cls(
            id=response.id,
            name=response.name,
            description=response.description,
            key_prefix=response.key_prefix,
            owner_id=response.owner_id,
            owner_name=response.owner_name,
            owner_type=response.owner_type,
            granted_permissions=list(response.granted_permissions),
            permission_names=list(response.granted_permissions),
            roles=[],
            scopes=list(response.scopes),
            status=response.status,
            permissions=permissions,
            last_used_at=response.last_used_at,
            expires_at=response.expires_at,
            revoked_at=response.revoked_at,
            created_at=response.created_at,
        )


class ApiKeyCreatedHttpResponse(BaseModel):
    id: str
    name: str
    description: str | None
    key_prefix: str
    owner_id: str
    owner_name: str | None = None
    owner_type: str
    granted_permissions: list[str]
    permission_names: list[str]
    roles: list[str]
    scopes: list[str]
    status: str
    permissions: ApiKeyPermissionHttpResponse | None = None
    last_used_at: str | None
    expires_at: str | None
    revoked_at: str | None
    created_at: str
    api_key: str
    token: str

    @classmethod
    def from_application(cls, response: ApiKeyCreatedResponse) -> ApiKeyCreatedHttpResponse:
        return cls(
            id=response.id,
            name=response.name,
            description=response.description,
            key_prefix=response.key_prefix,
            owner_id=response.owner_id,
            owner_name=response.owner_name,
            owner_type=response.owner_type,
            granted_permissions=list(response.granted_permissions),
            permission_names=list(response.granted_permissions),
            roles=[],
            scopes=list(response.scopes),
            status=response.status,
            permissions=None,
            last_used_at=response.last_used_at,
            expires_at=response.expires_at,
            revoked_at=response.revoked_at,
            created_at=response.created_at,
            api_key=response.api_key,
            token=response.api_key,
        )


class ApiKeyListHttpResponse(BaseModel):
    data: list[ApiKeyHttpResponse]
    pagination: PaginationHttpResponse
    permissions: ApiKeyPermissionHttpResponse
    success: bool = True

    @classmethod
    def from_application(cls, response: ApiKeyListResponse) -> ApiKeyListHttpResponse:
        permissions = ApiKeyPermissionHttpResponse.from_application(response.permissions)
        return cls(
            data=[
                ApiKeyHttpResponse.from_application(item, permissions=permissions)
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


class CurrentSessionUserHttpResponse(BaseModel):
    id: str
    type: str
    email: str | None
    name: str
    profile_label: str


class CurrentSessionHttpResponse(BaseModel):
    api_key_id: str
    auth_method: str
    expires_at: str | None
    issued_at: str
    user: CurrentSessionUserHttpResponse

    @classmethod
    def from_application(cls, response: CurrentSessionResponse) -> CurrentSessionHttpResponse:
        return cls(
            api_key_id=response.api_key_id,
            auth_method=response.auth_method,
            expires_at=response.expires_at,
            issued_at=response.issued_at,
            user=CurrentSessionUserHttpResponse(
                id=response.user_id,
                type=response.user_type,
                email=response.email,
                name=response.name,
                profile_label=response.profile_label,
            ),
        )


class UpdateProfileHttpRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: str | None = None
    name: str
    organization: str | None = None


class ChangePasswordHttpRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    current_password: str
    new_password: str


class ProfilePermissionHttpResponse(BaseModel):
    change_password: bool
    read: bool
    revoke_sessions: bool
    update: bool

    @classmethod
    def from_application(
        cls,
        response: ProfilePermissionsResponse,
    ) -> ProfilePermissionHttpResponse:
        return cls(
            change_password=response.change_password,
            read=response.read,
            revoke_sessions=response.revoke_sessions,
            update=response.update,
        )


class UserProfileHttpResponse(BaseModel):
    account_type: str
    avatar_url: str | None
    created_at: str | None
    email: str | None
    email_editable: bool
    id: str
    last_login_at: str | None
    name: str
    organization: str | None
    permissions: ProfilePermissionHttpResponse
    primary_role: str | None

    @classmethod
    def from_application(cls, response: UserProfileResponse) -> UserProfileHttpResponse:
        return cls(
            account_type=response.account_type,
            avatar_url=response.avatar_url,
            created_at=response.created_at,
            email=response.email,
            email_editable=response.email_editable,
            id=response.id,
            last_login_at=response.last_login_at,
            name=response.name,
            organization=response.organization,
            permissions=ProfilePermissionHttpResponse.from_application(response.permissions),
            primary_role=response.primary_role,
        )


class AccountSecurityHttpResponse(BaseModel):
    mfa_enabled: bool
    passkeys_enabled: bool
    password_change_available: bool
    recovery_keys_available: bool
    webauthn_enabled: bool

    @classmethod
    def from_application(cls, response: AccountSecurityResponse) -> AccountSecurityHttpResponse:
        return cls(
            mfa_enabled=response.mfa_enabled,
            passkeys_enabled=response.passkeys_enabled,
            password_change_available=response.password_change_available,
            recovery_keys_available=response.recovery_keys_available,
            webauthn_enabled=response.webauthn_enabled,
        )


class ActiveSessionHttpResponse(BaseModel):
    current: bool
    device: str | None
    expires_at: str | None
    id: str
    ip_address: str | None
    last_seen_at: str | None
    location: str | None
    user_agent: str | None

    @classmethod
    def from_application(cls, response: ActiveSessionResponse) -> ActiveSessionHttpResponse:
        return cls(
            current=response.current,
            device=response.device,
            expires_at=response.expires_at,
            id=response.id,
            ip_address=response.ip_address,
            last_seen_at=response.last_seen_at,
            location=response.location,
            user_agent=response.user_agent,
        )


class ActiveSessionListHttpResponse(BaseModel):
    data: list[ActiveSessionHttpResponse]
    permissions: ProfilePermissionHttpResponse

    @classmethod
    def from_application(
        cls,
        response: ActiveSessionListResponse,
    ) -> ActiveSessionListHttpResponse:
        return cls(
            data=[ActiveSessionHttpResponse.from_application(item) for item in response.data],
            permissions=ProfilePermissionHttpResponse.from_application(response.permissions),
        )


class UserPreferencesHttpResponse(BaseModel):
    date_time_format: str
    display_density: str
    language: str
    theme: str
    timezone: str

    @classmethod
    def from_application(cls, response: UserPreferencesResponse) -> UserPreferencesHttpResponse:
        return cls(
            date_time_format=response.date_time_format,
            display_density=response.display_density,
            language=response.language,
            theme=response.theme,
            timezone=response.timezone,
        )


class NotificationPreferencesHttpResponse(BaseModel):
    audit_alerts: bool
    email_enabled: bool
    in_app_enabled: bool
    product_updates: bool
    security_alerts: bool

    @classmethod
    def from_application(
        cls,
        response: NotificationPreferencesResponse,
    ) -> NotificationPreferencesHttpResponse:
        return cls(
            audit_alerts=response.audit_alerts,
            email_enabled=response.email_enabled,
            in_app_enabled=response.in_app_enabled,
            product_updates=response.product_updates,
            security_alerts=response.security_alerts,
        )


class PublicSettingsHttpResponse(BaseModel):
    api_status: str
    backend_version: str | None
    deployment_mode: str | None
    environment: str | None
    frontend_version: str | None
    instance_name: str | None
    public_url: str | None

    @classmethod
    def from_application(cls, response: PublicSettingsResponse) -> PublicSettingsHttpResponse:
        return cls(
            api_status=response.api_status,
            backend_version=response.backend_version,
            deployment_mode=response.deployment_mode,
            environment=response.environment,
            frontend_version=response.frontend_version,
            instance_name=response.instance_name,
            public_url=response.public_url,
        )


class SettingsPermissionHttpResponse(BaseModel):
    read: bool
    update: bool
    update_notifications: bool
    update_preferences: bool

    @classmethod
    def from_application(
        cls,
        response: SettingsPermissionsResponse,
    ) -> SettingsPermissionHttpResponse:
        return cls(
            read=response.read,
            update=response.update,
            update_notifications=response.update_notifications,
            update_preferences=response.update_preferences,
        )


class SettingsHttpResponse(BaseModel):
    notifications: NotificationPreferencesHttpResponse
    permissions: SettingsPermissionHttpResponse
    preferences: UserPreferencesHttpResponse
    public_settings: PublicSettingsHttpResponse

    @classmethod
    def from_application(cls, response: SettingsResponse) -> SettingsHttpResponse:
        return cls(
            notifications=NotificationPreferencesHttpResponse.from_application(
                response.notifications
            ),
            permissions=SettingsPermissionHttpResponse.from_application(response.permissions),
            preferences=UserPreferencesHttpResponse.from_application(response.preferences),
            public_settings=PublicSettingsHttpResponse.from_application(response.public_settings),
        )


class UpdatePreferencesHttpRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    date_time_format: str
    display_density: str
    language: str
    theme: str
    timezone: str


class UpdateNotificationsHttpRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    audit_alerts: bool
    email_enabled: bool
    in_app_enabled: bool
    product_updates: bool
    security_alerts: bool


class CreateRoleHttpRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str | None = None
    name: str
    permission_ids: list[str] = Field(default_factory=list)


class UpdateRoleHttpRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str | None = None
    name: str
    permission_ids: list[str] = Field(default_factory=list)


class PermissionHttpResponse(BaseModel):
    action: str
    description: str | None
    group: str
    id: str
    name: str
    resource: str
    sensitivity: str

    @classmethod
    def from_application(cls, response: PermissionResponse) -> PermissionHttpResponse:
        return cls(
            action=response.action,
            description=response.description,
            group=response.group,
            id=response.id,
            name=response.name,
            resource=response.resource,
            sensitivity=response.sensitivity,
        )


class RbacPermissionHttpResponse(BaseModel):
    assign: bool
    create: bool
    read: bool
    revoke: bool
    update: bool

    @classmethod
    def from_application(cls, response: RolePermissionsResponse) -> RbacPermissionHttpResponse:
        return cls(
            assign=response.assign,
            create=response.create,
            read=response.read,
            revoke=response.revoke,
            update=response.update,
        )


class RoleHttpResponse(BaseModel):
    assignments_count: int
    description: str | None
    id: str
    is_system: bool
    kind: str
    name: str
    permission_ids: list[str]
    permissions: list[PermissionHttpResponse]
    permissions_count: int
    status: str
    ui_permissions: RbacPermissionHttpResponse

    @classmethod
    def from_application(cls, response: RoleResponse) -> RoleHttpResponse:
        return cls(
            assignments_count=response.assignments_count,
            description=response.description,
            id=response.id,
            is_system=response.is_system,
            kind=response.kind,
            name=response.name,
            permission_ids=list(response.permission_ids),
            permissions=[
                PermissionHttpResponse.from_application(permission)
                for permission in response.permissions
            ],
            permissions_count=response.permissions_count,
            status=response.status,
            ui_permissions=RbacPermissionHttpResponse.from_application(response.ui_permissions),
        )


class RoleListHttpResponse(BaseModel):
    data: list[RoleHttpResponse]
    limit: int
    offset: int
    permissions: RbacPermissionHttpResponse
    total: int

    @classmethod
    def from_application(cls, response: RoleListResponse) -> RoleListHttpResponse:
        return cls(
            data=[RoleHttpResponse.from_application(role) for role in response.data],
            limit=response.limit,
            offset=response.offset,
            permissions=RbacPermissionHttpResponse.from_application(response.permissions),
            total=response.total,
        )


class PermissionListHttpResponse(BaseModel):
    data: list[PermissionHttpResponse]

    @classmethod
    def from_application(
        cls,
        response: PermissionListResponse,
    ) -> PermissionListHttpResponse:
        return cls(
            data=[
                PermissionHttpResponse.from_application(permission) for permission in response.data
            ]
        )


class UserRoleHttpResponse(BaseModel):
    actor_id: str
    assigned_at: str
    assigned_by: str | None
    id: str
    role_id: str
    role_name: str
    scope_id: str | None
    scope_type: str
    status: str

    @classmethod
    def from_application(cls, response: UserRoleResponse) -> UserRoleHttpResponse:
        return cls(
            actor_id=response.actor_id,
            assigned_at=response.assigned_at,
            assigned_by=response.assigned_by,
            id=response.id,
            role_id=response.role_id,
            role_name=response.role_name,
            scope_id=response.scope_id,
            scope_type=response.scope_type,
            status=response.status,
        )


class UserRoleListHttpResponse(BaseModel):
    actor_id: str
    data: list[UserRoleHttpResponse]
    permissions: RbacPermissionHttpResponse

    @classmethod
    def from_application(
        cls,
        response: UserRoleListResponse,
    ) -> UserRoleListHttpResponse:
        return cls(
            actor_id=response.actor_id,
            data=[UserRoleHttpResponse.from_application(item) for item in response.data],
            permissions=RbacPermissionHttpResponse.from_application(response.permissions),
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

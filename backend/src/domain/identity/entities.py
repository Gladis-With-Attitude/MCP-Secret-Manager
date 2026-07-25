from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from domain.identity.value_objects import (
    ApiKeyId,
    ApiKeyOwnerType,
    IdentityStatus,
    ServiceAccountId,
    ServiceAccountName,
    SessionId,
    UserDisplayName,
    UserEmail,
    UserId,
)
from domain.project.value_objects import ProjectId


@dataclass(frozen=True, slots=True, eq=False)
class User:
    id: UserId
    email: UserEmail
    display_name: UserDisplayName
    status: IdentityStatus
    created_at: datetime

    @classmethod
    def create(cls, email: UserEmail, display_name: UserDisplayName) -> User:
        return cls(
            id=UserId.new(),
            email=email,
            display_name=display_name,
            status=IdentityStatus.ACTIVE,
            created_at=datetime.now(UTC),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, User):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def update_display_name(self, display_name: UserDisplayName) -> User:
        return User(
            id=self.id,
            email=self.email,
            display_name=display_name,
            status=self.status,
            created_at=self.created_at,
        )


@dataclass(frozen=True, slots=True, eq=False)
class UserPreferences:
    user_id: UserId
    organization: str | None
    avatar_url: str | None
    theme: str
    language: str
    timezone: str
    date_time_format: str
    display_density: str
    audit_alerts: bool
    email_enabled: bool
    in_app_enabled: bool
    product_updates: bool
    security_alerts: bool

    @classmethod
    def default(cls, user_id: UserId) -> UserPreferences:
        return cls(
            user_id=user_id,
            organization=None,
            avatar_url=None,
            theme="system",
            language="en",
            timezone="UTC",
            date_time_format="absolute",
            display_density="comfortable",
            audit_alerts=True,
            email_enabled=True,
            in_app_enabled=True,
            product_updates=False,
            security_alerts=True,
        )

    def update_profile_metadata(
        self,
        *,
        organization: str | None,
    ) -> UserPreferences:
        return UserPreferences(
            user_id=self.user_id,
            organization=organization,
            avatar_url=self.avatar_url,
            theme=self.theme,
            language=self.language,
            timezone=self.timezone,
            date_time_format=self.date_time_format,
            display_density=self.display_density,
            audit_alerts=self.audit_alerts,
            email_enabled=self.email_enabled,
            in_app_enabled=self.in_app_enabled,
            product_updates=self.product_updates,
            security_alerts=self.security_alerts,
        )

    def update_preferences(
        self,
        *,
        theme: str,
        language: str,
        timezone: str,
        date_time_format: str,
        display_density: str,
    ) -> UserPreferences:
        return UserPreferences(
            user_id=self.user_id,
            organization=self.organization,
            avatar_url=self.avatar_url,
            theme=theme,
            language=language,
            timezone=timezone,
            date_time_format=date_time_format,
            display_density=display_density,
            audit_alerts=self.audit_alerts,
            email_enabled=self.email_enabled,
            in_app_enabled=self.in_app_enabled,
            product_updates=self.product_updates,
            security_alerts=self.security_alerts,
        )

    def update_notifications(
        self,
        *,
        audit_alerts: bool,
        email_enabled: bool,
        in_app_enabled: bool,
        product_updates: bool,
        security_alerts: bool,
    ) -> UserPreferences:
        return UserPreferences(
            user_id=self.user_id,
            organization=self.organization,
            avatar_url=self.avatar_url,
            theme=self.theme,
            language=self.language,
            timezone=self.timezone,
            date_time_format=self.date_time_format,
            display_density=self.display_density,
            audit_alerts=audit_alerts,
            email_enabled=email_enabled,
            in_app_enabled=in_app_enabled,
            product_updates=product_updates,
            security_alerts=security_alerts,
        )


@dataclass(frozen=True, slots=True, eq=False)
class ServiceAccount:
    id: ServiceAccountId
    project_id: ProjectId
    name: ServiceAccountName
    description: str | None
    status: IdentityStatus
    created_at: datetime

    @classmethod
    def create(
        cls,
        project_id: ProjectId,
        name: ServiceAccountName,
        description: str | None,
    ) -> ServiceAccount:
        return cls(
            id=ServiceAccountId.new(),
            project_id=project_id,
            name=name,
            description=description,
            status=IdentityStatus.ACTIVE,
            created_at=datetime.now(UTC),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ServiceAccount):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


@dataclass(frozen=True, slots=True, eq=False)
class ApiKey:
    id: ApiKeyId
    hashed_key: str
    key_prefix: str
    owner_id: UserId | ServiceAccountId
    owner_type: ApiKeyOwnerType
    expires_at: datetime | None
    revoked_at: datetime | None
    created_at: datetime
    name: str | None = None
    description: str | None = None
    granted_permissions: tuple[str, ...] = ()
    scopes: tuple[str, ...] = ()

    @classmethod
    def create(
        cls,
        hashed_key: str,
        key_prefix: str,
        owner_id: UserId | ServiceAccountId,
        owner_type: ApiKeyOwnerType,
        expires_at: datetime | None,
        name: str | None = None,
        description: str | None = None,
        granted_permissions: tuple[str, ...] = (),
        scopes: tuple[str, ...] = (),
    ) -> ApiKey:
        return cls(
            id=ApiKeyId.new(),
            hashed_key=hashed_key,
            key_prefix=key_prefix,
            owner_id=owner_id,
            owner_type=owner_type,
            expires_at=expires_at,
            revoked_at=None,
            created_at=datetime.now(UTC),
            name=name,
            description=description,
            granted_permissions=granted_permissions,
            scopes=scopes,
        )

    def is_revoked(self) -> bool:
        return self.revoked_at is not None

    def is_expired(self, now: datetime) -> bool:
        return self.expires_at is not None and self.expires_at <= now

    def revoke(self, now: datetime | None = None) -> ApiKey:
        if self.revoked_at is not None:
            return self
        return ApiKey(
            id=self.id,
            hashed_key=self.hashed_key,
            key_prefix=self.key_prefix,
            owner_id=self.owner_id,
            owner_type=self.owner_type,
            expires_at=self.expires_at,
            revoked_at=now or datetime.now(UTC),
            created_at=self.created_at,
            name=self.name,
            description=self.description,
            granted_permissions=self.granted_permissions,
            scopes=self.scopes,
        )

    def update_metadata(
        self,
        *,
        name: str | None,
        description: str | None,
        granted_permissions: tuple[str, ...],
        scopes: tuple[str, ...],
        expires_at: datetime | None,
    ) -> ApiKey:
        return ApiKey(
            id=self.id,
            hashed_key=self.hashed_key,
            key_prefix=self.key_prefix,
            owner_id=self.owner_id,
            owner_type=self.owner_type,
            expires_at=expires_at,
            revoked_at=self.revoked_at,
            created_at=self.created_at,
            name=name,
            description=description,
            granted_permissions=granted_permissions,
            scopes=scopes,
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ApiKey):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


@dataclass(frozen=True, slots=True, eq=False)
class AuthSession:
    id: SessionId
    hashed_token: str
    token_prefix: str
    api_key_id: ApiKeyId
    owner_id: UserId | ServiceAccountId
    owner_type: ApiKeyOwnerType
    expires_at: datetime | None
    revoked_at: datetime | None
    created_at: datetime
    last_seen_at: datetime | None

    @classmethod
    def create(
        cls,
        hashed_token: str,
        token_prefix: str,
        api_key_id: ApiKeyId,
        owner_id: UserId | ServiceAccountId,
        owner_type: ApiKeyOwnerType,
        expires_at: datetime | None,
    ) -> AuthSession:
        return cls(
            id=SessionId.new(),
            hashed_token=hashed_token,
            token_prefix=token_prefix,
            api_key_id=api_key_id,
            owner_id=owner_id,
            owner_type=owner_type,
            expires_at=expires_at,
            revoked_at=None,
            created_at=datetime.now(UTC),
            last_seen_at=None,
        )

    def is_revoked(self) -> bool:
        return self.revoked_at is not None

    def is_expired(self, now: datetime) -> bool:
        return self.expires_at is not None and self.expires_at <= now

    def revoke(self, now: datetime | None = None) -> AuthSession:
        return AuthSession(
            id=self.id,
            hashed_token=self.hashed_token,
            token_prefix=self.token_prefix,
            api_key_id=self.api_key_id,
            owner_id=self.owner_id,
            owner_type=self.owner_type,
            expires_at=self.expires_at,
            revoked_at=now or datetime.now(UTC),
            created_at=self.created_at,
            last_seen_at=self.last_seen_at,
        )

    def mark_seen(self, now: datetime | None = None) -> AuthSession:
        return AuthSession(
            id=self.id,
            hashed_token=self.hashed_token,
            token_prefix=self.token_prefix,
            api_key_id=self.api_key_id,
            owner_id=self.owner_id,
            owner_type=self.owner_type,
            expires_at=self.expires_at,
            revoked_at=self.revoked_at,
            created_at=self.created_at,
            last_seen_at=now or datetime.now(UTC),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AuthSession):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

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

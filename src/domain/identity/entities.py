from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from domain.identity.value_objects import (
    ApiKeyId,
    ApiKeyOwnerType,
    IdentityStatus,
    ServiceAccountId,
    ServiceAccountName,
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

    @classmethod
    def create(
        cls,
        hashed_key: str,
        key_prefix: str,
        owner_id: UserId | ServiceAccountId,
        owner_type: ApiKeyOwnerType,
        expires_at: datetime | None,
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
        )

    def is_revoked(self) -> bool:
        return self.revoked_at is not None

    def is_expired(self, now: datetime) -> bool:
        return self.expires_at is not None and self.expires_at <= now

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ApiKey):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

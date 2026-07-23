from __future__ import annotations

from typing import Protocol

from domain.identity.entities import ApiKey, AuthSession, ServiceAccount, User
from domain.identity.value_objects import (
    ApiKeyId,
    ServiceAccountId,
    ServiceAccountName,
    SessionId,
    UserEmail,
    UserId,
)
from domain.project.value_objects import ProjectId


class UserRepositoryConflictError(RuntimeError):
    """Raised when persistence detects a User constraint conflict."""


class ServiceAccountRepositoryConflictError(RuntimeError):
    """Raised when persistence detects a ServiceAccount constraint conflict."""


class ApiKeyRepositoryConflictError(RuntimeError):
    """Raised when persistence detects an ApiKey constraint conflict."""


class AuthSessionRepositoryConflictError(RuntimeError):
    """Raised when persistence detects an AuthSession constraint conflict."""


class UserRepository(Protocol):
    async def create(self, user: User) -> User:
        raise NotImplementedError

    async def get(self, user_id: UserId) -> User | None:
        raise NotImplementedError

    async def get_by_email(self, email: UserEmail) -> User | None:
        raise NotImplementedError


class ServiceAccountRepository(Protocol):
    async def create(self, service_account: ServiceAccount) -> ServiceAccount:
        raise NotImplementedError

    async def get(self, service_account_id: ServiceAccountId) -> ServiceAccount | None:
        raise NotImplementedError

    async def exists_in_project(self, project_id: ProjectId, name: ServiceAccountName) -> bool:
        raise NotImplementedError


class ApiKeyRepository(Protocol):
    async def create(self, api_key: ApiKey) -> ApiKey:
        raise NotImplementedError

    async def get(self, api_key_id: ApiKeyId) -> ApiKey | None:
        raise NotImplementedError

    async def get_by_prefix(self, key_prefix: str) -> ApiKey | None:
        raise NotImplementedError


class AuthSessionRepository(Protocol):
    async def create(self, session: AuthSession) -> AuthSession:
        raise NotImplementedError

    async def get(self, session_id: SessionId) -> AuthSession | None:
        raise NotImplementedError

    async def get_by_prefix(self, token_prefix: str) -> AuthSession | None:
        raise NotImplementedError

    async def update(self, session: AuthSession) -> AuthSession:
        raise NotImplementedError

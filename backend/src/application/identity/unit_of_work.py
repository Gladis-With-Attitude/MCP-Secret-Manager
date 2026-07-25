from __future__ import annotations

from types import TracebackType
from typing import Protocol

from domain.identity.repositories import (
    ApiKeyRepository,
    AuthSessionRepository,
    ServiceAccountRepository,
    UserPreferencesRepository,
    UserRepository,
)
from domain.project.repositories import ProjectRepository


class IdentityUnitOfWork(Protocol):
    @property
    def projects(self) -> ProjectRepository:
        raise NotImplementedError

    @property
    def users(self) -> UserRepository:
        raise NotImplementedError

    @property
    def user_preferences(self) -> UserPreferencesRepository:
        raise NotImplementedError

    @property
    def service_accounts(self) -> ServiceAccountRepository:
        raise NotImplementedError

    @property
    def api_keys(self) -> ApiKeyRepository:
        raise NotImplementedError

    @property
    def auth_sessions(self) -> AuthSessionRepository:
        raise NotImplementedError

    async def __aenter__(self) -> IdentityUnitOfWork:
        raise NotImplementedError

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        raise NotImplementedError

    async def commit(self) -> None:
        raise NotImplementedError

    async def rollback(self) -> None:
        raise NotImplementedError

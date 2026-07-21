from __future__ import annotations

from types import TracebackType
from typing import Protocol

from domain.project.repositories import ProjectRepository
from domain.secret.repositories import SecretRepository
from domain.vault.repositories import VaultRepository


class UnitOfWork(Protocol):
    @property
    def vaults(self) -> VaultRepository:
        raise NotImplementedError

    @property
    def projects(self) -> ProjectRepository:
        raise NotImplementedError

    @property
    def secrets(self) -> SecretRepository:
        raise NotImplementedError

    async def __aenter__(self) -> UnitOfWork:
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

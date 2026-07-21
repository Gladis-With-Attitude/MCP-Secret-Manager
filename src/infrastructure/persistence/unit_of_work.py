from __future__ import annotations

from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from domain.project.repositories import ProjectRepository
from domain.vault.repositories import VaultRepository
from infrastructure.persistence.project_repository import SqlAlchemyProjectRepository
from infrastructure.persistence.vault_repository import SqlAlchemyVaultRepository


class SqlAlchemyUnitOfWork:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        self._vaults: SqlAlchemyVaultRepository | None = None
        self._projects: SqlAlchemyProjectRepository | None = None

    @property
    def vaults(self) -> VaultRepository:
        if self._vaults is None:
            raise RuntimeError("Unit of Work has not been entered.")
        return self._vaults

    @property
    def projects(self) -> ProjectRepository:
        if self._projects is None:
            raise RuntimeError("Unit of Work has not been entered.")
        return self._projects

    async def __aenter__(self) -> Self:
        self._session = self._session_factory()
        self._vaults = SqlAlchemyVaultRepository(self._session)
        self._projects = SqlAlchemyProjectRepository(self._session)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            await self.rollback()

        await self._close()

    async def commit(self) -> None:
        session = self._get_session()
        await session.commit()

    async def rollback(self) -> None:
        session = self._get_session()
        await session.rollback()

    async def _close(self) -> None:
        session = self._get_session()
        await session.close()
        self._session = None
        self._vaults = None
        self._projects = None

    def _get_session(self) -> AsyncSession:
        if self._session is None:
            raise RuntimeError("Unit of Work has not been entered.")
        return self._session

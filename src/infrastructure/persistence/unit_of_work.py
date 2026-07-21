from __future__ import annotations

from types import TracebackType
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from domain.identity.repositories import ApiKeyRepository, ServiceAccountRepository, UserRepository
from domain.project.repositories import ProjectRepository
from domain.rbac.repositories import PermissionRepository, RoleAssignmentRepository, RoleRepository
from domain.secret.repositories import SecretRepository
from domain.secret_version.repositories import SecretVersionRepository
from domain.vault.repositories import VaultRepository
from infrastructure.persistence.identity_repositories import (
    SqlAlchemyApiKeyRepository,
    SqlAlchemyServiceAccountRepository,
    SqlAlchemyUserRepository,
)
from infrastructure.persistence.project_repository import SqlAlchemyProjectRepository
from infrastructure.persistence.rbac_repositories import (
    SqlAlchemyPermissionRepository,
    SqlAlchemyRoleAssignmentRepository,
    SqlAlchemyRoleRepository,
)
from infrastructure.persistence.secret_repository import SqlAlchemySecretRepository
from infrastructure.persistence.secret_version_repository import SqlAlchemySecretVersionRepository
from infrastructure.persistence.vault_repository import SqlAlchemyVaultRepository


class SqlAlchemyUnitOfWork:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        self._vaults: SqlAlchemyVaultRepository | None = None
        self._projects: SqlAlchemyProjectRepository | None = None
        self._secrets: SqlAlchemySecretRepository | None = None
        self._secret_versions: SqlAlchemySecretVersionRepository | None = None
        self._users: SqlAlchemyUserRepository | None = None
        self._service_accounts: SqlAlchemyServiceAccountRepository | None = None
        self._api_keys: SqlAlchemyApiKeyRepository | None = None
        self._permissions: SqlAlchemyPermissionRepository | None = None
        self._roles: SqlAlchemyRoleRepository | None = None
        self._role_assignments: SqlAlchemyRoleAssignmentRepository | None = None

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

    @property
    def secrets(self) -> SecretRepository:
        if self._secrets is None:
            raise RuntimeError("Unit of Work has not been entered.")
        return self._secrets

    @property
    def secret_versions(self) -> SecretVersionRepository:
        if self._secret_versions is None:
            raise RuntimeError("Unit of Work has not been entered.")
        return self._secret_versions

    @property
    def users(self) -> UserRepository:
        if self._users is None:
            raise RuntimeError("Unit of Work has not been entered.")
        return self._users

    @property
    def service_accounts(self) -> ServiceAccountRepository:
        if self._service_accounts is None:
            raise RuntimeError("Unit of Work has not been entered.")
        return self._service_accounts

    @property
    def api_keys(self) -> ApiKeyRepository:
        if self._api_keys is None:
            raise RuntimeError("Unit of Work has not been entered.")
        return self._api_keys

    @property
    def permissions(self) -> PermissionRepository:
        if self._permissions is None:
            raise RuntimeError("Unit of Work has not been entered.")
        return self._permissions

    @property
    def roles(self) -> RoleRepository:
        if self._roles is None:
            raise RuntimeError("Unit of Work has not been entered.")
        return self._roles

    @property
    def role_assignments(self) -> RoleAssignmentRepository:
        if self._role_assignments is None:
            raise RuntimeError("Unit of Work has not been entered.")
        return self._role_assignments

    async def __aenter__(self) -> Self:
        self._session = self._session_factory()
        self._vaults = SqlAlchemyVaultRepository(self._session)
        self._projects = SqlAlchemyProjectRepository(self._session)
        self._secrets = SqlAlchemySecretRepository(self._session)
        self._secret_versions = SqlAlchemySecretVersionRepository(self._session)
        self._users = SqlAlchemyUserRepository(self._session)
        self._service_accounts = SqlAlchemyServiceAccountRepository(self._session)
        self._api_keys = SqlAlchemyApiKeyRepository(self._session)
        self._permissions = SqlAlchemyPermissionRepository(self._session)
        self._roles = SqlAlchemyRoleRepository(self._session)
        self._role_assignments = SqlAlchemyRoleAssignmentRepository(self._session)
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
        self._secrets = None
        self._secret_versions = None
        self._users = None
        self._service_accounts = None
        self._api_keys = None
        self._permissions = None
        self._roles = None
        self._role_assignments = None

    def _get_session(self) -> AsyncSession:
        if self._session is None:
            raise RuntimeError("Unit of Work has not been entered.")
        return self._session

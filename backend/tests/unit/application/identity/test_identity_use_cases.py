from __future__ import annotations

from collections.abc import Sequence
from dataclasses import replace
from datetime import UTC, datetime, timedelta
from types import TracebackType
from typing import Self

import anyio
import pytest

from application.identity.dto import (
    CreateApiKeyRequest,
    CreateServiceAccountRequest,
    CreateUserRequest,
)
from application.identity.exceptions import AuthenticationFailedError, IdentityNotFoundError
from application.identity.use_cases import (
    AuthenticateApiKeyUseCase,
    CreateApiKeyUseCase,
    CreateServiceAccountUseCase,
    CreateUserUseCase,
)
from domain.identity.entities import ApiKey, ServiceAccount, User
from domain.identity.repositories import (
    ApiKeyRepositoryConflictError,
    ServiceAccountRepository,
    ServiceAccountRepositoryConflictError,
    UserRepository,
    UserRepositoryConflictError,
)
from domain.identity.value_objects import (
    ApiKeyId,
    ApiKeyOwnerType,
    ServiceAccountId,
    ServiceAccountName,
    UserEmail,
    UserId,
)
from domain.project.entities import Project
from domain.project.repositories import ProjectRepository, ProjectRepositoryConflictError
from domain.project.value_objects import ProjectId, ProjectName
from domain.secret.entities import Secret
from domain.secret.repositories import SecretRepository, SecretRepositoryConflictError
from domain.secret.value_objects import SecretId, SecretKey
from domain.secret_version.entities import SecretVersion
from domain.secret_version.repositories import (
    SecretVersionRepository,
    SecretVersionRepositoryConflictError,
)
from domain.secret_version.value_objects import SecretVersionId
from domain.vault.entities import Vault
from domain.vault.repositories import VaultRepository, VaultRepositoryConflictError
from domain.vault.value_objects import VaultId, VaultName


class InMemoryUserRepository:
    def __init__(self) -> None:
        self._users: dict[UserId, User] = {}

    async def create(self, user: User) -> User:
        if await self.get_by_email(user.email) is not None:
            raise UserRepositoryConflictError("User already exists.")
        self._users[user.id] = user
        return user

    async def get(self, user_id: UserId) -> User | None:
        return self._users.get(user_id)

    async def get_by_email(self, email: UserEmail) -> User | None:
        return next((user for user in self._users.values() if user.email == email), None)


class InMemoryServiceAccountRepository:
    def __init__(self) -> None:
        self._service_accounts: dict[ServiceAccountId, ServiceAccount] = {}

    async def create(self, service_account: ServiceAccount) -> ServiceAccount:
        if await self.exists_in_project(service_account.project_id, service_account.name):
            raise ServiceAccountRepositoryConflictError("Service account already exists.")
        self._service_accounts[service_account.id] = service_account
        return service_account

    async def get(self, service_account_id: ServiceAccountId) -> ServiceAccount | None:
        return self._service_accounts.get(service_account_id)

    async def exists_in_project(self, project_id: ProjectId, name: ServiceAccountName) -> bool:
        return any(
            service_account.project_id == project_id and service_account.name == name
            for service_account in self._service_accounts.values()
        )


class InMemoryApiKeyRepository:
    def __init__(self) -> None:
        self._api_keys: dict[ApiKeyId, ApiKey] = {}

    async def create(self, api_key: ApiKey) -> ApiKey:
        if await self.get_by_prefix(api_key.key_prefix) is not None:
            raise ApiKeyRepositoryConflictError("API key already exists.")
        self._api_keys[api_key.id] = api_key
        return api_key

    async def get(self, api_key_id: ApiKeyId) -> ApiKey | None:
        return self._api_keys.get(api_key_id)

    async def get_by_prefix(self, key_prefix: str) -> ApiKey | None:
        return next(
            (api_key for api_key in self._api_keys.values() if api_key.key_prefix == key_prefix),
            None,
        )

    async def replace(self, api_key: ApiKey) -> None:
        self._api_keys[api_key.id] = api_key


class InMemoryProjectRepository:
    def __init__(self) -> None:
        self._projects: dict[ProjectId, Project] = {}

    async def create(self, project: Project) -> Project:
        if await self.exists_in_vault(project.vault_id, project.name):
            raise ProjectRepositoryConflictError("Project already exists.")
        self._projects[project.id] = project
        return project

    async def get(self, project_id: ProjectId) -> Project | None:
        return self._projects.get(project_id)

    async def list_by_vault(self, vault_id: VaultId) -> Sequence[Project]:
        return tuple(project for project in self._projects.values() if project.vault_id == vault_id)

    async def exists_in_vault(self, vault_id: VaultId, name: ProjectName) -> bool:
        return any(
            project.vault_id == vault_id and project.name == name
            for project in self._projects.values()
        )


class UnusedVaultRepository:
    async def create(self, _vault: Vault) -> Vault:
        raise VaultRepositoryConflictError("Vault repository is not used in identity tests.")

    async def get(self, _vault_id: VaultId) -> Vault | None:
        return None

    async def list(self) -> Sequence[Vault]:
        return ()

    async def exists_by_name(self, _name: VaultName) -> bool:
        return False


class UnusedSecretRepository:
    async def create(self, _secret: Secret) -> Secret:
        raise SecretRepositoryConflictError("Secret repository is not used in identity tests.")

    async def get(self, _secret_id: SecretId) -> Secret | None:
        return None

    async def list_by_project(self, _project_id: ProjectId) -> Sequence[Secret]:
        return ()

    async def exists_in_project(self, _project_id: ProjectId, _key: SecretKey) -> bool:
        return False


class UnusedSecretVersionRepository:
    async def create(self, _secret_version: SecretVersion) -> SecretVersion:
        raise SecretVersionRepositoryConflictError(
            "SecretVersion repository is not used in identity tests."
        )

    async def get(self, _secret_version_id: SecretVersionId) -> SecretVersion | None:
        return None

    async def list_versions(self, _secret_id: SecretId) -> Sequence[SecretVersion]:
        return ()

    async def get_active(self, _secret_id: SecretId) -> SecretVersion | None:
        return None

    async def deactivate_previous_versions(self, _secret_id: SecretId) -> None:
        return None


class InMemoryUnitOfWork:
    def __init__(self) -> None:
        self._vaults = UnusedVaultRepository()
        self._projects = InMemoryProjectRepository()
        self._secrets = UnusedSecretRepository()
        self._secret_versions = UnusedSecretVersionRepository()
        self._users = InMemoryUserRepository()
        self._service_accounts = InMemoryServiceAccountRepository()
        self._api_keys = InMemoryApiKeyRepository()
        self.committed = False
        self.rolled_back = False

    @property
    def vaults(self) -> VaultRepository:
        return self._vaults

    @property
    def projects(self) -> ProjectRepository:
        return self._projects

    @property
    def secrets(self) -> SecretRepository:
        return self._secrets

    @property
    def secret_versions(self) -> SecretVersionRepository:
        return self._secret_versions

    @property
    def users(self) -> UserRepository:
        return self._users

    @property
    def service_accounts(self) -> ServiceAccountRepository:
        return self._service_accounts

    @property
    def api_keys(self) -> InMemoryApiKeyRepository:
        return self._api_keys

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            await self.rollback()

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True


class FixedApiKeyGenerator:
    raw_api_key = (
        "mcp_sm_0123456789abcdef_0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
    )
    key_prefix = "mcp_sm_0123456789abcdef"

    def generate(self) -> str:
        return self.raw_api_key

    def extract_prefix(self, api_key: str) -> str | None:
        if api_key != self.raw_api_key:
            return None
        return self.key_prefix


class FakeApiKeyHasher:
    def hash(self, api_key: str) -> str:
        return f"hash:{api_key}"

    def verify(self, api_key: str, hashed_key: str) -> bool:
        return hashed_key == self.hash(api_key)


async def create_user(unit_of_work: InMemoryUnitOfWork) -> UserId:
    response = await CreateUserUseCase(unit_of_work).execute(
        CreateUserRequest(email="USER@example.com", display_name="Ada Lovelace")
    )
    return UserId.from_string(response.id)


async def create_api_key_for_user(unit_of_work: InMemoryUnitOfWork) -> str:
    user_id = await create_user(unit_of_work)
    response = await CreateApiKeyUseCase(
        unit_of_work,
        FixedApiKeyGenerator(),
        FakeApiKeyHasher(),
    ).execute(
        CreateApiKeyRequest(
            owner_id=str(user_id),
            owner_type=ApiKeyOwnerType.USER.value,
            expires_at=None,
        )
    )
    return response.api_key


def test_create_user_creates_active_user() -> None:
    async def run() -> None:
        unit_of_work = InMemoryUnitOfWork()

        response = await CreateUserUseCase(unit_of_work).execute(
            CreateUserRequest(email="USER@example.com", display_name=" Ada Lovelace ")
        )

        assert response.email == "user@example.com"
        assert response.display_name == "Ada Lovelace"
        assert response.status == "active"
        assert unit_of_work.committed is True

    anyio.run(run)


def test_create_service_account_creates_active_project_identity() -> None:
    async def run() -> None:
        unit_of_work = InMemoryUnitOfWork()
        project = await unit_of_work.projects.create(
            Project.create(vault_id=VaultId.new(), name=ProjectName("API"))
        )

        response = await CreateServiceAccountUseCase(unit_of_work).execute(
            CreateServiceAccountRequest(
                project_id=str(project.id),
                name="openclaw-api",
                description="OpenClaw API service account.",
            )
        )

        assert response.project_id == str(project.id)
        assert response.name == "openclaw-api"
        assert response.status == "active"
        assert unit_of_work.committed is True

    anyio.run(run)


def test_create_service_account_rejects_missing_project() -> None:
    async def run() -> None:
        unit_of_work = InMemoryUnitOfWork()

        with pytest.raises(IdentityNotFoundError, match="Project"):
            await CreateServiceAccountUseCase(unit_of_work).execute(
                CreateServiceAccountRequest(
                    project_id=str(ProjectId.new()),
                    name="openclaw-api",
                    description=None,
                )
            )

    anyio.run(run)


def test_create_api_key_returns_full_key_once_and_stores_hash_only() -> None:
    async def run() -> None:
        unit_of_work = InMemoryUnitOfWork()
        user_id = await create_user(unit_of_work)

        response = await CreateApiKeyUseCase(
            unit_of_work,
            FixedApiKeyGenerator(),
            FakeApiKeyHasher(),
        ).execute(
            CreateApiKeyRequest(
                owner_id=str(user_id),
                owner_type=ApiKeyOwnerType.USER.value,
                expires_at=None,
            )
        )
        stored = await unit_of_work.api_keys.get_by_prefix(response.key_prefix)

        assert response.api_key == FixedApiKeyGenerator.raw_api_key
        assert response.key_prefix == FixedApiKeyGenerator.key_prefix
        assert stored is not None
        assert stored.hashed_key == f"hash:{FixedApiKeyGenerator.raw_api_key}"
        assert stored.hashed_key != response.api_key

    anyio.run(run)


def test_authenticate_api_key_accepts_valid_key() -> None:
    async def run() -> None:
        unit_of_work = InMemoryUnitOfWork()
        raw_api_key = await create_api_key_for_user(unit_of_work)

        response = await AuthenticateApiKeyUseCase(
            unit_of_work,
            FixedApiKeyGenerator(),
            FakeApiKeyHasher(),
        ).execute(raw_api_key)

        assert response.type == "user"
        assert response.id != ""
        assert response.api_key_id != ""

    anyio.run(run)


def test_authenticate_api_key_rejects_expired_key() -> None:
    async def run() -> None:
        unit_of_work = InMemoryUnitOfWork()
        raw_api_key = await create_api_key_for_user(unit_of_work)
        stored = await unit_of_work.api_keys.get_by_prefix(FixedApiKeyGenerator.key_prefix)
        assert stored is not None
        await unit_of_work.api_keys.replace(
            replace(stored, expires_at=datetime.now(UTC) - timedelta(seconds=1))
        )

        with pytest.raises(AuthenticationFailedError):
            await AuthenticateApiKeyUseCase(
                unit_of_work,
                FixedApiKeyGenerator(),
                FakeApiKeyHasher(),
            ).execute(raw_api_key)

    anyio.run(run)


def test_authenticate_api_key_rejects_revoked_key() -> None:
    async def run() -> None:
        unit_of_work = InMemoryUnitOfWork()
        raw_api_key = await create_api_key_for_user(unit_of_work)
        stored = await unit_of_work.api_keys.get_by_prefix(FixedApiKeyGenerator.key_prefix)
        assert stored is not None
        await unit_of_work.api_keys.replace(replace(stored, revoked_at=datetime.now(UTC)))

        with pytest.raises(AuthenticationFailedError):
            await AuthenticateApiKeyUseCase(
                unit_of_work,
                FixedApiKeyGenerator(),
                FakeApiKeyHasher(),
            ).execute(raw_api_key)

    anyio.run(run)


def test_authenticate_api_key_rejects_invalid_hash() -> None:
    async def run() -> None:
        unit_of_work = InMemoryUnitOfWork()
        raw_api_key = await create_api_key_for_user(unit_of_work)
        stored = await unit_of_work.api_keys.get_by_prefix(FixedApiKeyGenerator.key_prefix)
        assert stored is not None
        await unit_of_work.api_keys.replace(replace(stored, hashed_key="hash:different-key"))

        with pytest.raises(AuthenticationFailedError):
            await AuthenticateApiKeyUseCase(
                unit_of_work,
                FixedApiKeyGenerator(),
                FakeApiKeyHasher(),
            ).execute(raw_api_key)

    anyio.run(run)


def test_authenticate_api_key_rejects_unknown_key() -> None:
    async def run() -> None:
        unit_of_work = InMemoryUnitOfWork()

        with pytest.raises(AuthenticationFailedError):
            await AuthenticateApiKeyUseCase(
                unit_of_work,
                FixedApiKeyGenerator(),
                FakeApiKeyHasher(),
            ).execute(FixedApiKeyGenerator.raw_api_key)

    anyio.run(run)

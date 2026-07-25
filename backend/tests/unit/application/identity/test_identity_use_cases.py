from __future__ import annotations

import logging
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
    CreateSessionRequest,
    CreateUserRequest,
    GetApiKeyRequest,
    GetProfileRequest,
    GetSettingsRequest,
    ListActiveSessionsRequest,
    ListApiKeysRequest,
    RevokeApiKeyRequest,
    RevokeSessionRequest,
    UpdateApiKeyRequest,
    UpdateNotificationsRequest,
    UpdatePreferencesRequest,
    UpdateProfileRequest,
)
from application.identity.exceptions import (
    AuthenticationFailedError,
    IdentityNotFoundError,
    IdentityValidationError,
)
from application.identity.use_cases import (
    AuthenticateApiKeyUseCase,
    AuthenticateSessionUseCase,
    CreateApiKeyUseCase,
    CreateServiceAccountUseCase,
    CreateSessionUseCase,
    CreateUserUseCase,
    GetApiKeyUseCase,
    GetCurrentProfileUseCase,
    GetCurrentSessionUseCase,
    GetSettingsUseCase,
    ListActiveSessionsUseCase,
    ListApiKeysUseCase,
    RevokeApiKeyUseCase,
    RevokeCurrentSessionUseCase,
    RevokeSessionUseCase,
    UpdateApiKeyUseCase,
    UpdateCurrentProfileUseCase,
    UpdateNotificationsUseCase,
    UpdatePreferencesUseCase,
)
from domain.identity.entities import ApiKey, AuthSession, ServiceAccount, User, UserPreferences
from domain.identity.repositories import (
    ApiKeyRepositoryConflictError,
    AuthSessionRepositoryConflictError,
    ServiceAccountRepository,
    ServiceAccountRepositoryConflictError,
    UserPreferencesRepository,
    UserRepository,
    UserRepositoryConflictError,
)
from domain.identity.value_objects import (
    ApiKeyId,
    ApiKeyOwnerType,
    ServiceAccountId,
    ServiceAccountName,
    SessionId,
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

    async def update(self, user: User) -> User:
        if user.id not in self._users:
            raise UserRepositoryConflictError("User was not found.")
        self._users[user.id] = user
        return user


class InMemoryUserPreferencesRepository:
    def __init__(self) -> None:
        self._preferences: dict[UserId, UserPreferences] = {}

    async def get(self, user_id: UserId) -> UserPreferences | None:
        return self._preferences.get(user_id)

    async def upsert(self, preferences: UserPreferences) -> UserPreferences:
        self._preferences[preferences.user_id] = preferences
        return preferences


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

    async def list(
        self,
        *,
        limit: int = 20,
        offset: int = 0,
        search: str | None = None,
        status: str | None = None,
        now: datetime | None = None,
    ) -> tuple[ApiKey, ...]:
        api_keys = self._filtered(search=search, status=status, now=now)
        return api_keys[offset : offset + limit]

    async def count(
        self,
        *,
        search: str | None = None,
        status: str | None = None,
        now: datetime | None = None,
    ) -> int:
        return len(self._filtered(search=search, status=status, now=now))

    async def update(self, api_key: ApiKey) -> ApiKey:
        self._api_keys[api_key.id] = api_key
        return api_key

    async def replace(self, api_key: ApiKey) -> None:
        self._api_keys[api_key.id] = api_key

    def _filtered(
        self,
        *,
        search: str | None,
        status: str | None,
        now: datetime | None,
    ) -> tuple[ApiKey, ...]:
        effective_now = now or datetime.now(UTC)
        api_keys = tuple(sorted(self._api_keys.values(), key=lambda api_key: api_key.created_at))
        if search:
            needle = search.lower()
            api_keys = tuple(
                api_key
                for api_key in api_keys
                if needle in api_key.key_prefix.lower()
                or (api_key.name is not None and needle in api_key.name.lower())
                or needle in api_key.owner_type.value
            )
        if status == "active":
            api_keys = tuple(
                api_key
                for api_key in api_keys
                if not api_key.is_revoked() and not api_key.is_expired(effective_now)
            )
        elif status == "expired":
            api_keys = tuple(
                api_key
                for api_key in api_keys
                if not api_key.is_revoked() and api_key.is_expired(effective_now)
            )
        elif status == "revoked":
            api_keys = tuple(api_key for api_key in api_keys if api_key.is_revoked())
        elif status == "unknown":
            api_keys = ()
        return api_keys


class InMemoryAuthSessionRepository:
    def __init__(self) -> None:
        self._auth_sessions: dict[SessionId, AuthSession] = {}

    async def create(self, auth_session: AuthSession) -> AuthSession:
        if await self.get_by_prefix(auth_session.token_prefix) is not None:
            raise AuthSessionRepositoryConflictError("Session already exists.")
        self._auth_sessions[auth_session.id] = auth_session
        return auth_session

    async def get(self, session_id: SessionId) -> AuthSession | None:
        return self._auth_sessions.get(session_id)

    async def get_by_prefix(self, token_prefix: str) -> AuthSession | None:
        return next(
            (
                auth_session
                for auth_session in self._auth_sessions.values()
                if auth_session.token_prefix == token_prefix
            ),
            None,
        )

    async def list_for_owner(
        self,
        owner_id: UserId | ServiceAccountId,
        owner_type: ApiKeyOwnerType,
        now: datetime | None = None,
    ) -> tuple[AuthSession, ...]:
        effective_now = now or datetime.now(UTC)
        return tuple(
            auth_session
            for auth_session in self._auth_sessions.values()
            if auth_session.owner_id == owner_id
            and auth_session.owner_type is owner_type
            and not auth_session.is_revoked()
            and not auth_session.is_expired(effective_now)
        )

    async def update(self, auth_session: AuthSession) -> AuthSession:
        self._auth_sessions[auth_session.id] = auth_session
        return auth_session


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

    async def update(self, project: Project) -> Project:
        self._projects[project.id] = project
        return project

    async def list_by_vault(
        self,
        vault_id: VaultId,
        *,
        include_archived: bool = False,
        limit: int = 20,
        offset: int = 0,
        search: str | None = None,
        status: str | None = None,
    ) -> Sequence[Project]:
        projects = [project for project in self._projects.values() if project.vault_id == vault_id]
        if status == "archived":
            projects = [project for project in projects if project.archived]
        elif status == "active" or not include_archived:
            projects = [project for project in projects if not project.archived]
        if search:
            projects = [
                project for project in projects if search.lower() in project.name.value.lower()
            ]
        return tuple(projects[offset : offset + limit])

    async def count_by_vault(
        self,
        vault_id: VaultId,
        *,
        include_archived: bool = False,
        search: str | None = None,
        status: str | None = None,
    ) -> int:
        return len(
            await self.list_by_vault(
                vault_id,
                include_archived=include_archived,
                limit=10_000,
                offset=0,
                search=search,
                status=status,
            )
        )

    async def exists_in_vault(
        self,
        vault_id: VaultId,
        name: ProjectName,
        *,
        exclude_project_id: ProjectId | None = None,
    ) -> bool:
        return any(
            project.vault_id == vault_id
            and project.name == name
            and project.id != exclude_project_id
            for project in self._projects.values()
        )


class UnusedVaultRepository:
    async def create(self, _vault: Vault) -> Vault:
        raise VaultRepositoryConflictError("Vault repository is not used in identity tests.")

    async def get(self, _vault_id: VaultId) -> Vault | None:
        return None

    async def update(self, _vault: Vault) -> Vault:
        raise VaultRepositoryConflictError("Vault repository is not used in identity tests.")

    async def list(
        self,
        *,
        include_archived: bool = False,
        limit: int = 20,
        offset: int = 0,
        search: str | None = None,
        status: str | None = None,
    ) -> Sequence[Vault]:
        _ = include_archived, limit, offset, search, status
        return ()

    async def count(
        self,
        *,
        include_archived: bool = False,
        search: str | None = None,
        status: str | None = None,
    ) -> int:
        _ = include_archived, search, status
        return 0

    async def exists_by_name(
        self,
        _name: VaultName,
        *,
        exclude_vault_id: VaultId | None = None,
    ) -> bool:
        _ = exclude_vault_id
        return False


class UnusedSecretRepository:
    async def create(self, _secret: Secret) -> Secret:
        raise SecretRepositoryConflictError("Secret repository is not used in identity tests.")

    async def get(self, _secret_id: SecretId) -> Secret | None:
        return None

    async def update(self, _secret: Secret) -> Secret:
        raise SecretRepositoryConflictError("Secret repository is not used in Identity tests.")

    async def list_by_project(
        self,
        _project_id: ProjectId,
        *,
        include_archived: bool = False,
        limit: int = 20,
        offset: int = 0,
        search: str | None = None,
        status: str | None = None,
        secret_type: str | None = None,
    ) -> Sequence[Secret]:
        _ = include_archived, limit, offset, search, status, secret_type
        return ()

    async def count_by_project(
        self,
        _project_id: ProjectId,
        *,
        include_archived: bool = False,
        search: str | None = None,
        status: str | None = None,
        secret_type: str | None = None,
    ) -> int:
        _ = include_archived, search, status, secret_type
        return 0

    async def exists_in_project(
        self,
        _project_id: ProjectId,
        _key: SecretKey,
        *,
        exclude_secret_id: SecretId | None = None,
    ) -> bool:
        _ = exclude_secret_id
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

    async def activate(self, _secret_version_id: SecretVersionId) -> SecretVersion:
        raise SecretVersionRepositoryConflictError(
            "SecretVersion repository is not used in identity tests."
        )


class InMemoryUnitOfWork:
    def __init__(self) -> None:
        self._vaults = UnusedVaultRepository()
        self._projects = InMemoryProjectRepository()
        self._secrets = UnusedSecretRepository()
        self._secret_versions = UnusedSecretVersionRepository()
        self._users = InMemoryUserRepository()
        self._user_preferences = InMemoryUserPreferencesRepository()
        self._service_accounts = InMemoryServiceAccountRepository()
        self._api_keys = InMemoryApiKeyRepository()
        self._auth_sessions = InMemoryAuthSessionRepository()
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
    def user_preferences(self) -> UserPreferencesRepository:
        return self._user_preferences

    @property
    def service_accounts(self) -> ServiceAccountRepository:
        return self._service_accounts

    @property
    def api_keys(self) -> InMemoryApiKeyRepository:
        return self._api_keys

    @property
    def auth_sessions(self) -> InMemoryAuthSessionRepository:
        return self._auth_sessions

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


FAKE_BROWSER_SESSION_VALUE = (
    "mcp_sm_session_0123456789abcdef_"
    "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
)
FAKE_BROWSER_SESSION_PREFIX = "mcp_sm_session_0123456789abcdef"


class FixedSessionTokenGenerator:
    raw_session_token = FAKE_BROWSER_SESSION_VALUE
    token_prefix = FAKE_BROWSER_SESSION_PREFIX

    def generate(self) -> str:
        return self.raw_session_token

    def extract_prefix(self, session_token: str) -> str | None:
        if session_token != self.raw_session_token:
            return None
        return self.token_prefix


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
                name="agent",
                description="Production agent",
                granted_permissions=("secret.read",),
                scopes=("global",),
            )
        )
        stored = await unit_of_work.api_keys.get_by_prefix(response.key_prefix)

        assert response.api_key == FixedApiKeyGenerator.raw_api_key
        assert response.key_prefix == FixedApiKeyGenerator.key_prefix
        assert response.name == "agent"
        assert response.granted_permissions == ("secret.read",)
        assert response.scopes == ("global",)
        assert stored is not None
        assert stored.name == "agent"
        assert stored.description == "Production agent"
        assert stored.hashed_key == f"hash:{FixedApiKeyGenerator.raw_api_key}"
        assert stored.hashed_key != response.api_key

    anyio.run(run)


def test_list_get_and_revoke_api_keys_return_metadata_only() -> None:
    async def run() -> None:
        unit_of_work = InMemoryUnitOfWork()
        user_id = await create_user(unit_of_work)
        created = await CreateApiKeyUseCase(
            unit_of_work,
            FixedApiKeyGenerator(),
            FakeApiKeyHasher(),
        ).execute(
            CreateApiKeyRequest(
                owner_id=str(user_id),
                owner_type=ApiKeyOwnerType.USER.value,
                expires_at=None,
                name="agent",
                description="Production agent",
                granted_permissions=("secret.read",),
                scopes=("global",),
            )
        )

        listed = await ListApiKeysUseCase(unit_of_work).execute(
            ListApiKeysRequest(search="agent", status="active")
        )
        detail = await GetApiKeyUseCase(unit_of_work).execute(
            GetApiKeyRequest(api_key_id=created.id)
        )
        revoked = await RevokeApiKeyUseCase(unit_of_work).execute(
            RevokeApiKeyRequest(api_key_id=created.id)
        )

        assert listed.pagination.total == 1
        assert listed.data[0].id == created.id
        assert listed.data[0].name == "agent"
        assert detail.key_prefix == FixedApiKeyGenerator.key_prefix
        assert revoked.status == "revoked"
        assert revoked.revoked_at is not None
        assert not hasattr(revoked, "api_key")

    anyio.run(run)


def test_create_api_key_persists_metadata() -> None:
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
                name="Build agent",
                description="CI access",
                granted_permissions=("secret.read",),
                scopes=("project:alpha",),
            )
        )
        stored = await unit_of_work.api_keys.get_by_prefix(response.key_prefix)

        assert response.name == "Build agent"
        assert response.granted_permissions == ("secret.read",)
        assert response.scopes == ("project:alpha",)
        assert stored is not None
        assert stored.description == "CI access"

    anyio.run(run)


def test_list_api_keys_filters_and_paginates_metadata() -> None:
    async def run() -> None:
        unit_of_work = InMemoryUnitOfWork()
        user_id = await create_user(unit_of_work)
        await CreateApiKeyUseCase(
            unit_of_work,
            FixedApiKeyGenerator(),
            FakeApiKeyHasher(),
        ).execute(
            CreateApiKeyRequest(
                owner_id=str(user_id),
                owner_type=ApiKeyOwnerType.USER.value,
                expires_at=None,
                name="Build agent",
                description=None,
            )
        )

        response = await ListApiKeysUseCase(unit_of_work).execute(
            ListApiKeysRequest(search="build", status="active")
        )

        assert response.pagination.total == 1
        assert response.data[0].name == "Build agent"
        assert response.permissions.read is True
        assert response.permissions.update is True

    anyio.run(run)


def test_update_api_key_changes_metadata_without_exposing_secret() -> None:
    async def run() -> None:
        unit_of_work = InMemoryUnitOfWork()
        raw_api_key = await create_api_key_for_user(unit_of_work)
        stored = await unit_of_work.api_keys.get_by_prefix(FixedApiKeyGenerator.key_prefix)
        assert stored is not None

        updated = await UpdateApiKeyUseCase(unit_of_work).execute(
            UpdateApiKeyRequest(
                api_key_id=str(stored.id),
                name="Updated agent",
                description="Updated metadata",
                expires_at=None,
                granted_permissions=("secret.read", "secret.rotate"),
                scopes=("global",),
            )
        )

        assert updated.name == "Updated agent"
        assert updated.description == "Updated metadata"
        assert updated.granted_permissions == ("secret.read", "secret.rotate")
        assert updated.scopes == ("global",)
        assert not hasattr(updated, "api_key")
        assert raw_api_key not in repr(updated)

    anyio.run(run)


def test_get_and_revoke_api_key() -> None:
    async def run() -> None:
        unit_of_work = InMemoryUnitOfWork()
        raw_api_key = await create_api_key_for_user(unit_of_work)
        stored = await unit_of_work.api_keys.get_by_prefix(FixedApiKeyGenerator.key_prefix)
        assert stored is not None

        fetched = await GetApiKeyUseCase(unit_of_work).execute(GetApiKeyRequest(str(stored.id)))
        revoked = await RevokeApiKeyUseCase(unit_of_work).execute(RevokeApiKeyRequest(fetched.id))

        assert raw_api_key == FixedApiKeyGenerator.raw_api_key
        assert fetched.key_prefix == FixedApiKeyGenerator.key_prefix
        assert revoked.status == "revoked"
        assert unit_of_work.committed is True

    anyio.run(run)


def test_authenticate_api_key_accepts_valid_key(caplog: pytest.LogCaptureFixture) -> None:
    async def run() -> None:
        unit_of_work = InMemoryUnitOfWork()
        raw_api_key = await create_api_key_for_user(unit_of_work)

        caplog.set_level(logging.INFO, logger="application.identity.use_cases")
        response = await AuthenticateApiKeyUseCase(
            unit_of_work,
            FixedApiKeyGenerator(),
            FakeApiKeyHasher(),
        ).execute(raw_api_key)

        assert response.type == "user"
        assert response.id != ""
        assert response.api_key_id != ""
        assert FixedApiKeyGenerator.raw_api_key not in caplog.text
        assert any(
            getattr(record, "event_fields", {}).items()
            >= {
                "event": "api_key_authenticate",
                "result": "success",
                "resource_id": response.api_key_id,
                "owner_id": response.id,
                "owner_type": response.type,
            }.items()
            for record in caplog.records
        )

    anyio.run(run)


def test_get_current_session_returns_authenticated_user_metadata() -> None:
    async def run() -> None:
        unit_of_work = InMemoryUnitOfWork()
        raw_api_key = await create_api_key_for_user(unit_of_work)
        authenticated = await AuthenticateApiKeyUseCase(
            unit_of_work,
            FixedApiKeyGenerator(),
            FakeApiKeyHasher(),
        ).execute(raw_api_key)

        response = await GetCurrentSessionUseCase(unit_of_work).execute(authenticated.api_key_id)

        assert response.auth_method == "api_key"
        assert response.api_key_id == authenticated.api_key_id
        assert response.user_id == authenticated.id
        assert response.user_type == "user"
        assert response.email == "user@example.com"
        assert response.name == "Ada Lovelace"
        assert response.profile_label == "User"
        assert response.issued_at
        assert response.expires_at is None

    anyio.run(run)


def test_get_current_session_rejects_missing_api_key() -> None:
    async def run() -> None:
        unit_of_work = InMemoryUnitOfWork()
        await create_user(unit_of_work)

        with pytest.raises(AuthenticationFailedError, match="Invalid session"):
            await GetCurrentSessionUseCase(unit_of_work).execute(str(ApiKeyId.new()))

    anyio.run(run)


def test_create_and_authenticate_session_persists_hash_only() -> None:
    async def run() -> None:
        unit_of_work = InMemoryUnitOfWork()
        raw_api_key = await create_api_key_for_user(unit_of_work)

        created = await CreateSessionUseCase(
            unit_of_work,
            FixedApiKeyGenerator(),
            FakeApiKeyHasher(),
            FixedSessionTokenGenerator(),
            FakeApiKeyHasher(),
        ).execute(CreateSessionRequest(api_key=raw_api_key))
        stored = await unit_of_work.auth_sessions.get_by_prefix(
            FixedSessionTokenGenerator.token_prefix
        )
        authenticated = await AuthenticateSessionUseCase(
            unit_of_work,
            FixedSessionTokenGenerator(),
            FakeApiKeyHasher(),
        ).execute(created.session_token)

        assert created.session.user_id == authenticated.id
        assert authenticated.session_id is not None
        assert stored is not None
        assert stored.hashed_token == f"hash:{FixedSessionTokenGenerator.raw_session_token}"
        assert stored.hashed_token != created.session_token

    anyio.run(run)


def test_revoke_current_session_rejects_future_session_authentication() -> None:
    async def run() -> None:
        unit_of_work = InMemoryUnitOfWork()
        raw_api_key = await create_api_key_for_user(unit_of_work)
        created = await CreateSessionUseCase(
            unit_of_work,
            FixedApiKeyGenerator(),
            FakeApiKeyHasher(),
            FixedSessionTokenGenerator(),
            FakeApiKeyHasher(),
        ).execute(CreateSessionRequest(api_key=raw_api_key))
        authenticated = await AuthenticateSessionUseCase(
            unit_of_work,
            FixedSessionTokenGenerator(),
            FakeApiKeyHasher(),
        ).execute(created.session_token)

        await RevokeCurrentSessionUseCase(unit_of_work).execute(authenticated.session_id)

        with pytest.raises(AuthenticationFailedError):
            await AuthenticateSessionUseCase(
                unit_of_work,
                FixedSessionTokenGenerator(),
                FakeApiKeyHasher(),
            ).execute(created.session_token)

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


def test_authenticate_api_key_rejects_invalid_hash(
    caplog: pytest.LogCaptureFixture,
) -> None:
    async def run() -> None:
        unit_of_work = InMemoryUnitOfWork()
        raw_api_key = await create_api_key_for_user(unit_of_work)
        stored = await unit_of_work.api_keys.get_by_prefix(FixedApiKeyGenerator.key_prefix)
        assert stored is not None
        await unit_of_work.api_keys.replace(replace(stored, hashed_key="hash:different-key"))

        caplog.set_level(logging.WARNING, logger="application.identity.use_cases")
        with pytest.raises(AuthenticationFailedError):
            await AuthenticateApiKeyUseCase(
                unit_of_work,
                FixedApiKeyGenerator(),
                FakeApiKeyHasher(),
            ).execute(raw_api_key)

        assert raw_api_key not in caplog.text
        assert FixedApiKeyGenerator.key_prefix not in caplog.text
        assert any(
            getattr(record, "event_fields", {}).items()
            >= {
                "event": "api_key_authenticate",
                "result": "failure",
                "reason": "invalid_key",
            }.items()
            for record in caplog.records
        )

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


def test_get_and_update_current_profile_persist_safe_user_metadata() -> None:
    async def run() -> None:
        unit_of_work = InMemoryUnitOfWork()
        user_id = await create_user(unit_of_work)

        updated = await UpdateCurrentProfileUseCase(unit_of_work).execute(
            UpdateProfileRequest(
                identity_id=str(user_id),
                identity_type=ApiKeyOwnerType.USER.value,
                email="user@example.com",
                name="Ada Byron",
                organization="Analytical Engines",
            )
        )
        fetched = await GetCurrentProfileUseCase(unit_of_work).execute(
            GetProfileRequest(identity_id=str(user_id), identity_type=ApiKeyOwnerType.USER.value)
        )

        assert updated.name == "Ada Byron"
        assert updated.organization == "Analytical Engines"
        assert updated.email_editable is False
        assert updated.permissions.update is True
        assert fetched.name == "Ada Byron"
        assert fetched.organization == "Analytical Engines"

    anyio.run(run)


def test_update_current_profile_rejects_email_changes() -> None:
    async def run() -> None:
        unit_of_work = InMemoryUnitOfWork()
        user_id = await create_user(unit_of_work)

        with pytest.raises(IdentityValidationError, match="email cannot be changed"):
            await UpdateCurrentProfileUseCase(unit_of_work).execute(
                UpdateProfileRequest(
                    identity_id=str(user_id),
                    identity_type=ApiKeyOwnerType.USER.value,
                    email="other@example.com",
                    name="Ada Byron",
                    organization=None,
                )
            )

    anyio.run(run)


def test_settings_preferences_and_notifications_round_trip() -> None:
    async def run() -> None:
        unit_of_work = InMemoryUnitOfWork()
        user_id = await create_user(unit_of_work)

        settings = await GetSettingsUseCase(unit_of_work).execute(
            GetSettingsRequest(identity_id=str(user_id), identity_type=ApiKeyOwnerType.USER.value)
        )
        preferences = await UpdatePreferencesUseCase(unit_of_work).execute(
            UpdatePreferencesRequest(
                identity_id=str(user_id),
                identity_type=ApiKeyOwnerType.USER.value,
                date_time_format="relative",
                display_density="compact",
                language="fr",
                theme="dark",
                timezone="Europe/Paris",
            )
        )
        notifications = await UpdateNotificationsUseCase(unit_of_work).execute(
            UpdateNotificationsRequest(
                identity_id=str(user_id),
                identity_type=ApiKeyOwnerType.USER.value,
                audit_alerts=False,
                email_enabled=False,
                in_app_enabled=True,
                product_updates=True,
                security_alerts=True,
            )
        )
        refreshed = await GetSettingsUseCase(unit_of_work).execute(
            GetSettingsRequest(identity_id=str(user_id), identity_type=ApiKeyOwnerType.USER.value)
        )

        assert settings.preferences.theme == "system"
        assert preferences.theme == "dark"
        assert preferences.timezone == "Europe/Paris"
        assert notifications.audit_alerts is False
        assert refreshed.preferences.display_density == "compact"
        assert refreshed.notifications.product_updates is True

    anyio.run(run)


def test_list_and_revoke_own_sessions_never_exposes_tokens() -> None:
    async def run() -> None:
        unit_of_work = InMemoryUnitOfWork()
        raw_api_key = await create_api_key_for_user(unit_of_work)
        created = await CreateSessionUseCase(
            unit_of_work,
            FixedApiKeyGenerator(),
            FakeApiKeyHasher(),
            FixedSessionTokenGenerator(),
            FakeApiKeyHasher(),
        ).execute(CreateSessionRequest(api_key=raw_api_key))
        authenticated = await AuthenticateSessionUseCase(
            unit_of_work,
            FixedSessionTokenGenerator(),
            FakeApiKeyHasher(),
        ).execute(created.session_token)

        listed = await ListActiveSessionsUseCase(unit_of_work).execute(
            ListActiveSessionsRequest(
                identity_id=authenticated.id,
                identity_type=authenticated.type,
                current_session_id=authenticated.session_id,
            )
        )
        assert listed.data[0].current is True
        assert not hasattr(listed.data[0], "token")
        assert FixedSessionTokenGenerator.raw_session_token not in repr(listed)

        assert authenticated.session_id is not None
        await RevokeSessionUseCase(unit_of_work).execute(
            RevokeSessionRequest(
                identity_id=authenticated.id,
                identity_type=authenticated.type,
                session_id=authenticated.session_id,
                current_session_id=authenticated.session_id,
            )
        )
        after_revoke = await ListActiveSessionsUseCase(unit_of_work).execute(
            ListActiveSessionsRequest(
                identity_id=authenticated.id,
                identity_type=authenticated.type,
                current_session_id=authenticated.session_id,
            )
        )
        assert after_revoke.data == ()

    anyio.run(run)

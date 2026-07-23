from __future__ import annotations

from collections.abc import AsyncIterator, Sequence
from types import TracebackType
from typing import Self

import anyio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient, Response

from application.crypto.use_cases import DecryptSecretValueUseCase, EncryptSecretValueUseCase
from application.project.use_cases import GetProjectUseCase
from application.rbac.dto import RequirePermission
from application.rbac.exceptions import AuthorizationDeniedError
from application.secret.use_cases import GetSecretUseCase
from application.secret_version.use_cases import (
    CreateSecretVersionUseCase,
    GetActiveSecretVersionUseCase,
    ListSecretVersionsUseCase,
)
from domain.crypto.entities import EncryptedSecretValue, SecretEncryptionContext
from domain.project.entities import Project
from domain.project.repositories import ProjectRepository, ProjectRepositoryConflictError
from domain.project.value_objects import ProjectId, ProjectName
from domain.secret.entities import Secret
from domain.secret.repositories import SecretRepository, SecretRepositoryConflictError
from domain.secret.value_objects import SecretDescription, SecretId, SecretKey
from domain.secret_version.entities import SecretVersion
from domain.secret_version.repositories import (
    SecretVersionRepository,
    SecretVersionRepositoryConflictError,
)
from domain.secret_version.value_objects import SecretValue, SecretVersionId
from domain.vault.entities import Vault
from domain.vault.repositories import VaultRepository, VaultRepositoryConflictError
from domain.vault.value_objects import VaultId, VaultName
from presentation.rest.app import create_app
from presentation.rest.authentication import AuthenticatedIdentity, get_authenticated_identity
from presentation.rest.dependencies import (
    get_active_secret_version_use_case,
    get_authorize_use_case,
    get_create_secret_version_use_case,
    get_list_secret_versions_use_case,
    get_project_use_case,
    get_secret_use_case,
)


class InMemoryVaultRepository:
    async def create(self, _vault: Vault) -> Vault:
        raise VaultRepositoryConflictError(
            "Vault repository is not used in SecretVersion REST tests."
        )

    async def get(self, _vault_id: VaultId) -> Vault | None:
        return None

    async def update(self, _vault: Vault) -> Vault:
        raise VaultRepositoryConflictError(
            "Vault repository is not used in SecretVersion REST tests."
        )

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


class InMemoryProjectRepository:
    def __init__(self) -> None:
        self._projects: dict[ProjectId, Project] = {}

    async def create(self, project: Project) -> Project:
        if await self.exists_in_vault(project.vault_id, project.name):
            raise ProjectRepositoryConflictError("Project name already exists.")
        self._projects[project.id] = project
        return project

    async def get(self, project_id: ProjectId) -> Project | None:
        return self._projects.get(project_id)

    async def update(self, project: Project) -> Project:
        return project

    async def list_by_vault(
        self,
        _vault_id: VaultId,
        *,
        include_archived: bool = False,
        limit: int = 20,
        offset: int = 0,
        search: str | None = None,
        status: str | None = None,
    ) -> Sequence[Project]:
        _ = include_archived, limit, offset, search, status
        projects = tuple(
            project for project in self._projects.values() if project.vault_id == _vault_id
        )
        return projects[offset : offset + limit]

    async def count_by_vault(
        self,
        _vault_id: VaultId,
        *,
        include_archived: bool = False,
        search: str | None = None,
        status: str | None = None,
    ) -> int:
        _ = include_archived, search, status
        return len(
            await self.list_by_vault(
                _vault_id,
                include_archived=include_archived,
                limit=10_000,
                offset=0,
                search=search,
                status=status,
            )
        )

    async def exists_in_vault(
        self,
        _vault_id: VaultId,
        _name: ProjectName,
        *,
        exclude_project_id: ProjectId | None = None,
    ) -> bool:
        return any(
            project.vault_id == _vault_id
            and project.name == _name
            and project.id != exclude_project_id
            for project in self._projects.values()
        )


class InMemorySecretRepository:
    def __init__(self) -> None:
        self._secrets: dict[SecretId, Secret] = {}

    async def create(self, secret: Secret) -> Secret:
        if await self.exists_in_project(secret.project_id, secret.key):
            raise SecretRepositoryConflictError("Secret key already exists.")
        self._secrets[secret.id] = secret
        return secret

    async def get(self, secret_id: SecretId) -> Secret | None:
        return self._secrets.get(secret_id)

    async def update(self, secret: Secret) -> Secret:
        if await self.exists_in_project(
            secret.project_id,
            secret.key,
            exclude_secret_id=secret.id,
        ):
            raise SecretRepositoryConflictError("Secret key already exists.")
        self._secrets[secret.id] = secret
        return secret

    async def list_by_project(
        self,
        project_id: ProjectId,
        *,
        include_archived: bool = False,
        limit: int = 20,
        offset: int = 0,
        search: str | None = None,
        status: str | None = None,
        secret_type: str | None = None,
    ) -> Sequence[Secret]:
        _ = include_archived, search, status, secret_type
        secrets = tuple(
            secret for secret in self._secrets.values() if secret.project_id == project_id
        )
        return secrets[offset : offset + limit]

    async def count_by_project(
        self,
        project_id: ProjectId,
        *,
        include_archived: bool = False,
        search: str | None = None,
        status: str | None = None,
        secret_type: str | None = None,
    ) -> int:
        return len(
            await self.list_by_project(
                project_id,
                include_archived=include_archived,
                limit=10_000,
                offset=0,
                search=search,
                status=status,
                secret_type=secret_type,
            )
        )

    async def exists_in_project(
        self,
        project_id: ProjectId,
        key: SecretKey,
        *,
        exclude_secret_id: SecretId | None = None,
    ) -> bool:
        return any(
            secret.project_id == project_id and secret.key == key and secret.id != exclude_secret_id
            for secret in self._secrets.values()
        )


class InMemorySecretVersionRepository:
    def __init__(self) -> None:
        self._versions: dict[SecretVersionId, SecretVersion] = {}

    async def create(self, secret_version: SecretVersion) -> SecretVersion:
        if any(
            version.secret_id == secret_version.secret_id
            and version.version == secret_version.version
            for version in self._versions.values()
        ):
            raise SecretVersionRepositoryConflictError("Secret version already exists.")
        if secret_version.active and await self.get_active(secret_version.secret_id) is not None:
            raise SecretVersionRepositoryConflictError("Active secret version already exists.")
        self._versions[secret_version.id] = secret_version
        return secret_version

    async def get(self, secret_version_id: SecretVersionId) -> SecretVersion | None:
        return self._versions.get(secret_version_id)

    async def list_versions(self, secret_id: SecretId) -> Sequence[SecretVersion]:
        return tuple(
            sorted(
                (version for version in self._versions.values() if version.secret_id == secret_id),
                key=lambda version: version.version.value,
            )
        )

    async def get_active(self, secret_id: SecretId) -> SecretVersion | None:
        return next(
            (
                version
                for version in self._versions.values()
                if version.secret_id == secret_id and version.active
            ),
            None,
        )

    async def deactivate_previous_versions(self, secret_id: SecretId) -> None:
        for version_id, version in tuple(self._versions.items()):
            if version.secret_id == secret_id and version.active:
                self._versions[version_id] = version.deactivate()


class FakeCryptoProvider:
    def encrypt_secret_value(
        self,
        _value: SecretValue,
        context: SecretEncryptionContext,
    ) -> EncryptedSecretValue:
        ciphertext = f"ciphertext:{context.secret_id}:{context.version}".encode()
        return EncryptedSecretValue(
            encrypted_value=ciphertext,
            encrypted_dek=f"wrapped-dek:{context.secret_id}:{context.version}".encode(),
            nonce=f"{context.version:012d}".encode(),
            authentication_tag=b"0" * 16,
            encryption_algorithm="AES-256-GCM",
            key_version=1,
        )

    def decrypt_secret_value(
        self,
        _encrypted_value: EncryptedSecretValue,
        context: SecretEncryptionContext,
    ) -> SecretValue:
        return SecretValue(f"plain-value-v{context.version}")


class InMemoryUnitOfWork:
    def __init__(
        self,
        projects: ProjectRepository,
        secrets: SecretRepository,
        secret_versions: SecretVersionRepository,
    ) -> None:
        self._vaults = InMemoryVaultRepository()
        self._projects = projects
        self._secrets = secrets
        self._secret_versions = secret_versions

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
        return None

    async def rollback(self) -> None:
        return None


class FakeAuthorizeUseCase:
    def __init__(self, *, allowed: bool = True) -> None:
        self.allowed = allowed
        self.requests: list[RequirePermission] = []

    async def execute(self, request: RequirePermission) -> None:
        self.requests.append(request)
        if not self.allowed:
            raise AuthorizationDeniedError("Permission denied.")


async def build_app_with_secret(
    *,
    authorize_use_case: FakeAuthorizeUseCase | None = None,
) -> tuple[FastAPI, Secret]:
    secrets = InMemorySecretRepository()
    secret_versions = InMemorySecretVersionRepository()
    projects = InMemoryProjectRepository()
    project = await projects.create(Project.create(vault_id=VaultId.new(), name=ProjectName("API")))
    secret = await secrets.create(
        Secret.create(
            project_id=project.id,
            key=SecretKey("OPENAI_API_KEY"),
            description=SecretDescription(None),
        )
    )
    unit_of_work = InMemoryUnitOfWork(projects, secrets, secret_versions)
    crypto_provider = FakeCryptoProvider()
    app = create_app(service_name="test-service")
    resolved_authorize_use_case = authorize_use_case or FakeAuthorizeUseCase()
    app.state.authorize_use_case = resolved_authorize_use_case

    async def create_dependency() -> AsyncIterator[CreateSecretVersionUseCase]:
        yield CreateSecretVersionUseCase(
            unit_of_work,
            EncryptSecretValueUseCase(crypto_provider),
        )

    async def list_dependency() -> AsyncIterator[ListSecretVersionsUseCase]:
        yield ListSecretVersionsUseCase(
            unit_of_work,
        )

    async def latest_dependency() -> AsyncIterator[GetActiveSecretVersionUseCase]:
        yield GetActiveSecretVersionUseCase(
            unit_of_work,
            DecryptSecretValueUseCase(crypto_provider),
        )

    async def get_secret_dependency() -> AsyncIterator[GetSecretUseCase]:
        yield GetSecretUseCase(unit_of_work)

    async def get_project_dependency() -> AsyncIterator[GetProjectUseCase]:
        yield GetProjectUseCase(unit_of_work)

    app.dependency_overrides[get_create_secret_version_use_case] = create_dependency
    app.dependency_overrides[get_list_secret_versions_use_case] = list_dependency
    app.dependency_overrides[get_active_secret_version_use_case] = latest_dependency
    app.dependency_overrides[get_secret_use_case] = get_secret_dependency
    app.dependency_overrides[get_project_use_case] = get_project_dependency
    app.dependency_overrides[get_authenticated_identity] = lambda: AuthenticatedIdentity(
        id=str(VaultId.new()),
        type="user",
        api_key_id=str(VaultId.new()),
    )
    app.dependency_overrides[get_authorize_use_case] = lambda: resolved_authorize_use_case
    return app, secret


async def post_secret_version(app: FastAPI, secret_id: str, value: str) -> Response:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        return await client.post(f"/v1/secrets/{secret_id}/versions", json={"value": value})


async def get_secret_versions(app: FastAPI, secret_id: str) -> Response:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        return await client.get(f"/v1/secrets/{secret_id}/versions")


async def get_latest_secret_version(app: FastAPI, secret_id: str) -> Response:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        return await client.get(f"/v1/secrets/{secret_id}/versions/latest")


def test_create_secret_version_endpoint_returns_created_v1() -> None:
    async def run() -> None:
        app, secret = await build_app_with_secret()

        response = await post_secret_version(app, str(secret.id), "plain-value-v1")

        assert response.status_code == 201
        payload = response.json()
        assert payload["secret_id"] == str(secret.id)
        assert "value" not in payload
        assert payload["version"] == 1
        assert payload["active"] is True
        assert isinstance(payload["id"], str)
        assert isinstance(payload["created_at"], str)
        assert app.state.authorize_use_case.requests[-1].permission == "secret.rotate"
        assert app.state.authorize_use_case.requests[-1].scope_type == "secret"
        assert app.state.authorize_use_case.requests[-1].scope_id == str(secret.id)
        assert app.state.authorize_use_case.requests[-1].parent_project_id == str(secret.project_id)

    anyio.run(run)


def test_secret_version_endpoints_return_history_and_latest() -> None:
    async def run() -> None:
        app, secret = await build_app_with_secret()
        first_response = await post_secret_version(app, str(secret.id), "plain-value-v1")
        second_response = await post_secret_version(app, str(secret.id), "plain-value-v2")

        history_response = await get_secret_versions(app, str(secret.id))
        latest_response = await get_latest_secret_version(app, str(secret.id))

        assert first_response.status_code == 201
        assert second_response.status_code == 201
        assert history_response.status_code == 200
        assert latest_response.status_code == 200
        history = history_response.json()
        latest = latest_response.json()
        assert [version["version"] for version in history] == [1, 2]
        assert [version["active"] for version in history] == [False, True]
        assert "value" not in history[0]
        assert "value" not in history[1]
        assert latest["id"] == second_response.json()["id"]
        assert latest["version"] == 2
        assert latest["active"] is True
        assert latest["value"] == "plain-value-v2"
        assert [request.permission for request in app.state.authorize_use_case.requests] == [
            "secret.rotate",
            "secret.rotate",
            "secret.read",
            "secret.decrypt",
        ]

    anyio.run(run)


def test_secret_version_endpoint_returns_forbidden_when_permission_is_denied() -> None:
    async def run() -> None:
        app, secret = await build_app_with_secret(
            authorize_use_case=FakeAuthorizeUseCase(allowed=False)
        )

        response = await get_latest_secret_version(app, str(secret.id))

        assert response.status_code == 403
        assert response.json() == {"detail": "Permission denied."}
        assert app.state.authorize_use_case.requests[-1].parent_project_id == str(secret.project_id)

    anyio.run(run)


def test_secret_version_endpoint_requires_identity() -> None:
    async def run() -> None:
        app, secret = await build_app_with_secret()
        app.dependency_overrides.pop(get_authenticated_identity)

        response = await get_latest_secret_version(app, str(secret.id))

        assert response.status_code == 401
        assert response.json() == {"detail": "Authentication is required."}

    anyio.run(run)


def test_create_secret_version_endpoint_returns_bad_request_for_invalid_secret_id() -> None:
    async def run() -> None:
        app, _secret = await build_app_with_secret()

        response = await post_secret_version(app, "not-a-uuid", "plain-value")

        assert response.status_code == 400
        assert response.json() == {"detail": "Secret id must be a valid UUID."}

    anyio.run(run)


def test_create_secret_version_endpoint_returns_bad_request_for_empty_value() -> None:
    async def run() -> None:
        app, secret = await build_app_with_secret()

        response = await post_secret_version(app, str(secret.id), "")

        assert response.status_code == 400
        assert response.json() == {"detail": "Secret value is required."}

    anyio.run(run)


def test_create_secret_version_endpoint_returns_not_found_for_missing_secret() -> None:
    async def run() -> None:
        app, _secret = await build_app_with_secret()

        response = await post_secret_version(app, str(SecretId.new()), "plain-value")

        assert response.status_code == 404
        assert response.json() == {"detail": "Secret not found."}

    anyio.run(run)


def test_get_latest_secret_version_endpoint_returns_not_found_without_active_version() -> None:
    async def run() -> None:
        app, secret = await build_app_with_secret()

        response = await get_latest_secret_version(app, str(secret.id))

        assert response.status_code == 404
        assert response.json() == {"detail": "Active secret version not found."}

    anyio.run(run)

from __future__ import annotations

from collections.abc import AsyncIterator, Sequence
from types import TracebackType
from typing import Self

import anyio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient, Response

from application.crypto.use_cases import DecryptSecretValueUseCase, EncryptSecretValueUseCase
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
from presentation.rest.dependencies import (
    get_active_secret_version_use_case,
    get_create_secret_version_use_case,
    get_list_secret_versions_use_case,
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
    async def create(self, _project: Project) -> Project:
        raise ProjectRepositoryConflictError(
            "Project repository is not used in SecretVersion REST tests."
        )

    async def get(self, _project_id: ProjectId) -> Project | None:
        return None

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
        return ()

    async def count_by_vault(
        self,
        _vault_id: VaultId,
        *,
        include_archived: bool = False,
        search: str | None = None,
        status: str | None = None,
    ) -> int:
        _ = include_archived, search, status
        return 0

    async def exists_in_vault(
        self,
        _vault_id: VaultId,
        _name: ProjectName,
        *,
        exclude_project_id: ProjectId | None = None,
    ) -> bool:
        _ = exclude_project_id
        return False


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

    async def list_by_project(self, project_id: ProjectId) -> Sequence[Secret]:
        return tuple(secret for secret in self._secrets.values() if secret.project_id == project_id)

    async def exists_in_project(self, project_id: ProjectId, key: SecretKey) -> bool:
        return any(
            secret.project_id == project_id and secret.key == key
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
        secrets: SecretRepository,
        secret_versions: SecretVersionRepository,
    ) -> None:
        self._vaults = InMemoryVaultRepository()
        self._projects = InMemoryProjectRepository()
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


async def build_app_with_secret() -> tuple[FastAPI, Secret]:
    secrets = InMemorySecretRepository()
    secret_versions = InMemorySecretVersionRepository()
    secret = await secrets.create(
        Secret.create(
            project_id=ProjectId.new(),
            key=SecretKey("OPENAI_API_KEY"),
            description=SecretDescription(None),
        )
    )
    unit_of_work = InMemoryUnitOfWork(secrets, secret_versions)
    crypto_provider = FakeCryptoProvider()
    app = create_app(service_name="test-service")

    async def create_dependency() -> AsyncIterator[CreateSecretVersionUseCase]:
        yield CreateSecretVersionUseCase(
            unit_of_work,
            EncryptSecretValueUseCase(crypto_provider),
        )

    async def list_dependency() -> AsyncIterator[ListSecretVersionsUseCase]:
        yield ListSecretVersionsUseCase(
            unit_of_work,
            DecryptSecretValueUseCase(crypto_provider),
        )

    async def latest_dependency() -> AsyncIterator[GetActiveSecretVersionUseCase]:
        yield GetActiveSecretVersionUseCase(
            unit_of_work,
            DecryptSecretValueUseCase(crypto_provider),
        )

    app.dependency_overrides[get_create_secret_version_use_case] = create_dependency
    app.dependency_overrides[get_list_secret_versions_use_case] = list_dependency
    app.dependency_overrides[get_active_secret_version_use_case] = latest_dependency
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
        assert payload["value"] == "plain-value-v1"
        assert payload["version"] == 1
        assert payload["active"] is True
        assert isinstance(payload["id"], str)
        assert isinstance(payload["created_at"], str)

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
        assert [version["value"] for version in history] == [
            "plain-value-v1",
            "plain-value-v2",
        ]
        assert latest["id"] == second_response.json()["id"]
        assert latest["version"] == 2
        assert latest["active"] is True

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

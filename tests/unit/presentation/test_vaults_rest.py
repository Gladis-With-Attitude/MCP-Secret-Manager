from __future__ import annotations

from collections.abc import AsyncIterator, Sequence
from types import TracebackType
from typing import Self

import anyio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient, Response

from application.vault.use_cases import CreateVaultUseCase
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
from presentation.rest.app import create_app
from presentation.rest.dependencies import get_create_vault_use_case


class InMemoryVaultRepository:
    def __init__(self) -> None:
        self._vaults: dict[VaultId, Vault] = {}

    async def create(self, vault: Vault) -> Vault:
        if await self.exists_by_name(vault.name):
            raise VaultRepositoryConflictError("Vault name already exists.")
        self._vaults[vault.id] = vault
        return vault

    async def get(self, vault_id: VaultId) -> Vault | None:
        return self._vaults.get(vault_id)

    async def list(self) -> Sequence[Vault]:
        return tuple(self._vaults.values())

    async def exists_by_name(self, name: VaultName) -> bool:
        return any(vault.name == name for vault in self._vaults.values())


class InMemoryProjectRepository:
    async def create(self, _project: Project) -> Project:
        raise ProjectRepositoryConflictError("Project repository is not used in Vault tests.")

    async def get(self, _project_id: ProjectId) -> Project | None:
        return None

    async def list_by_vault(self, _vault_id: VaultId) -> Sequence[Project]:
        return ()

    async def exists_in_vault(self, _vault_id: VaultId, _name: ProjectName) -> bool:
        return False


class InMemorySecretRepository:
    async def create(self, _secret: Secret) -> Secret:
        raise SecretRepositoryConflictError("Secret repository is not used in Vault tests.")

    async def get(self, _secret_id: SecretId) -> Secret | None:
        return None

    async def list_by_project(self, _project_id: ProjectId) -> Sequence[Secret]:
        return ()

    async def exists_in_project(self, _project_id: ProjectId, _key: SecretKey) -> bool:
        return False


class InMemorySecretVersionRepository:
    async def create(self, _secret_version: SecretVersion) -> SecretVersion:
        raise SecretVersionRepositoryConflictError(
            "SecretVersion repository is not used in Vault tests."
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
    def __init__(self, repository: VaultRepository) -> None:
        self._repository = repository
        self._projects = InMemoryProjectRepository()
        self._secrets = InMemorySecretRepository()
        self._secret_versions = InMemorySecretVersionRepository()

    @property
    def vaults(self) -> VaultRepository:
        return self._repository

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
        return None

    async def commit(self) -> None:
        return None

    async def rollback(self) -> None:
        return None


def build_app(repository: InMemoryVaultRepository) -> FastAPI:
    app = create_app(service_name="test-service")

    async def dependency() -> AsyncIterator[CreateVaultUseCase]:
        yield CreateVaultUseCase(InMemoryUnitOfWork(repository))

    app.dependency_overrides[get_create_vault_use_case] = dependency
    return app


async def post_vault(app: FastAPI, payload: dict[str, str]) -> Response:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        return await client.post("/v1/vaults", json=payload)


def test_create_vault_endpoint_returns_created_vault() -> None:
    app = build_app(InMemoryVaultRepository())

    response = anyio.run(post_vault, app, {"name": "  Production  "})

    assert response.status_code == 201
    assert response.json()["name"] == "Production"
    assert isinstance(response.json()["id"], str)


def test_create_vault_endpoint_returns_bad_request_for_invalid_name() -> None:
    app = build_app(InMemoryVaultRepository())

    response = anyio.run(post_vault, app, {"name": "ab"})

    assert response.status_code == 400
    assert response.json() == {"detail": "Vault name must contain at least 3 characters."}


def test_create_vault_endpoint_returns_conflict_for_duplicate_name() -> None:
    app = build_app(InMemoryVaultRepository())
    first_response = anyio.run(post_vault, app, {"name": "Production"})

    second_response = anyio.run(post_vault, app, {"name": "Production"})

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json() == {"detail": "A vault with this name already exists."}

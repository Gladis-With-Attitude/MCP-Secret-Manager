from __future__ import annotations

from collections.abc import AsyncIterator, Sequence
from types import TracebackType
from typing import Self

import anyio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient, Response

from application.project.use_cases import CreateProjectUseCase
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
from presentation.rest.dependencies import get_create_project_use_case


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

    async def update(self, vault: Vault) -> Vault:
        if await self.exists_by_name(vault.name, exclude_vault_id=vault.id):
            raise VaultRepositoryConflictError("Vault name already exists.")
        self._vaults[vault.id] = vault
        return vault

    async def list(
        self,
        *,
        include_archived: bool = False,
        limit: int = 20,
        offset: int = 0,
        search: str | None = None,
        status: str | None = None,
    ) -> Sequence[Vault]:
        _ = include_archived, search, status
        vaults = tuple(self._vaults.values())
        return vaults[offset : offset + limit]

    async def count(
        self,
        *,
        include_archived: bool = False,
        search: str | None = None,
        status: str | None = None,
    ) -> int:
        _ = include_archived, search, status
        return len(self._vaults)

    async def exists_by_name(
        self,
        name: VaultName,
        *,
        exclude_vault_id: VaultId | None = None,
    ) -> bool:
        return any(
            vault.name == name and vault.id != exclude_vault_id for vault in self._vaults.values()
        )


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
        _ = search
        projects = tuple(
            project for project in self._projects.values() if project.vault_id == vault_id
        )
        if status == "archived":
            projects = tuple(project for project in projects if project.archived)
        elif status == "active" or not include_archived:
            projects = tuple(project for project in projects if not project.archived)
        return projects[offset : offset + limit]

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
                limit=1000,
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


class InMemorySecretRepository:
    async def create(self, _secret: Secret) -> Secret:
        raise SecretRepositoryConflictError("Secret repository is not used in Project tests.")

    async def get(self, _secret_id: SecretId) -> Secret | None:
        return None

    async def list_by_project(self, _project_id: ProjectId) -> Sequence[Secret]:
        return ()

    async def exists_in_project(self, _project_id: ProjectId, _key: SecretKey) -> bool:
        return False


class InMemorySecretVersionRepository:
    async def create(self, _secret_version: SecretVersion) -> SecretVersion:
        raise SecretVersionRepositoryConflictError(
            "SecretVersion repository is not used in Project tests."
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
    def __init__(self, vaults: VaultRepository, projects: ProjectRepository) -> None:
        self._vaults = vaults
        self._projects = projects
        self._secrets = InMemorySecretRepository()
        self._secret_versions = InMemorySecretVersionRepository()

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
        return None

    async def commit(self) -> None:
        return None

    async def rollback(self) -> None:
        return None


async def build_app_with_vault() -> tuple[FastAPI, Vault]:
    vaults = InMemoryVaultRepository()
    projects = InMemoryProjectRepository()
    vault = await vaults.create(Vault.create(VaultName("Production")))
    unit_of_work = InMemoryUnitOfWork(vaults, projects)
    app = create_app(service_name="test-service")

    async def dependency() -> AsyncIterator[CreateProjectUseCase]:
        yield CreateProjectUseCase(unit_of_work)

    app.dependency_overrides[get_create_project_use_case] = dependency
    return app, vault


async def post_project(app: FastAPI, vault_id: str, payload: dict[str, str]) -> Response:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        return await client.post(f"/v1/vaults/{vault_id}/projects", json=payload)


def test_create_project_endpoint_returns_created_project() -> None:
    async def run() -> None:
        app, vault = await build_app_with_vault()

        response = await post_project(app, str(vault.id), {"name": "  API  "})

        assert response.status_code == 201
        assert response.json()["vault_id"] == str(vault.id)
        assert response.json()["name"] == "API"
        assert isinstance(response.json()["id"], str)

    anyio.run(run)


def test_create_project_endpoint_returns_bad_request_for_invalid_vault_id() -> None:
    async def run() -> None:
        app, _vault = await build_app_with_vault()

        response = await post_project(app, "not-a-uuid", {"name": "API"})

        assert response.status_code == 400
        assert response.json() == {"detail": "Vault id must be a valid UUID."}

    anyio.run(run)


def test_create_project_endpoint_returns_bad_request_for_invalid_name() -> None:
    async def run() -> None:
        app, vault = await build_app_with_vault()

        response = await post_project(app, str(vault.id), {"name": "ab"})

        assert response.status_code == 400
        assert response.json() == {"detail": "Project name must contain at least 3 characters."}

    anyio.run(run)


def test_create_project_endpoint_returns_not_found_for_missing_vault() -> None:
    async def run() -> None:
        app, _vault = await build_app_with_vault()

        response = await post_project(app, str(VaultId.new()), {"name": "API"})

        assert response.status_code == 404
        assert response.json() == {"detail": "Vault not found."}

    anyio.run(run)


def test_create_project_endpoint_returns_conflict_for_duplicate_name_in_vault() -> None:
    async def run() -> None:
        app, vault = await build_app_with_vault()
        first_response = await post_project(app, str(vault.id), {"name": "API"})

        second_response = await post_project(app, str(vault.id), {"name": "API"})

        assert first_response.status_code == 201
        assert second_response.status_code == 409
        assert second_response.json() == {
            "detail": "A project with this name already exists in this vault."
        }

    anyio.run(run)

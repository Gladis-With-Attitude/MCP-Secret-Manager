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

    async def list(self) -> Sequence[Vault]:
        return tuple(self._vaults.values())

    async def exists_by_name(self, name: VaultName) -> bool:
        return any(vault.name == name for vault in self._vaults.values())


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

    async def list_by_vault(self, vault_id: VaultId) -> Sequence[Project]:
        return tuple(project for project in self._projects.values() if project.vault_id == vault_id)

    async def exists_in_vault(self, vault_id: VaultId, name: ProjectName) -> bool:
        return any(
            project.vault_id == vault_id and project.name == name
            for project in self._projects.values()
        )


class InMemoryUnitOfWork:
    def __init__(self, vaults: VaultRepository, projects: ProjectRepository) -> None:
        self._vaults = vaults
        self._projects = projects

    @property
    def vaults(self) -> VaultRepository:
        return self._vaults

    @property
    def projects(self) -> ProjectRepository:
        return self._projects

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

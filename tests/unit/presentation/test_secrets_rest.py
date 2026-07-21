from __future__ import annotations

from collections.abc import AsyncIterator, Sequence
from types import TracebackType
from typing import Self

import anyio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient, Response

from application.secret.use_cases import CreateSecretUseCase
from domain.project.entities import Project
from domain.project.repositories import ProjectRepository, ProjectRepositoryConflictError
from domain.project.value_objects import ProjectId, ProjectName
from domain.secret.entities import Secret
from domain.secret.repositories import SecretRepository, SecretRepositoryConflictError
from domain.secret.value_objects import SecretId, SecretKey
from domain.vault.entities import Vault
from domain.vault.repositories import VaultRepository, VaultRepositoryConflictError
from domain.vault.value_objects import VaultId, VaultName
from presentation.rest.app import create_app
from presentation.rest.dependencies import get_create_secret_use_case


class InMemoryVaultRepository:
    async def create(self, _vault: Vault) -> Vault:
        raise VaultRepositoryConflictError("Vault repository is not used in Secret REST tests.")

    async def get(self, _vault_id: VaultId) -> Vault | None:
        return None

    async def list(self) -> Sequence[Vault]:
        return ()

    async def exists_by_name(self, _name: VaultName) -> bool:
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

    async def list_by_vault(self, vault_id: VaultId) -> Sequence[Project]:
        return tuple(project for project in self._projects.values() if project.vault_id == vault_id)

    async def exists_in_vault(self, vault_id: VaultId, name: ProjectName) -> bool:
        return any(
            project.vault_id == vault_id and project.name == name
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

    async def list_by_project(self, project_id: ProjectId) -> Sequence[Secret]:
        return tuple(secret for secret in self._secrets.values() if secret.project_id == project_id)

    async def exists_in_project(self, project_id: ProjectId, key: SecretKey) -> bool:
        return any(
            secret.project_id == project_id and secret.key == key
            for secret in self._secrets.values()
        )


class InMemoryUnitOfWork:
    def __init__(self, projects: ProjectRepository, secrets: SecretRepository) -> None:
        self._vaults = InMemoryVaultRepository()
        self._projects = projects
        self._secrets = secrets

    @property
    def vaults(self) -> VaultRepository:
        return self._vaults

    @property
    def projects(self) -> ProjectRepository:
        return self._projects

    @property
    def secrets(self) -> SecretRepository:
        return self._secrets

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


async def build_app_with_project() -> tuple[FastAPI, Project]:
    projects = InMemoryProjectRepository()
    secrets = InMemorySecretRepository()
    project = await projects.create(Project.create(vault_id=VaultId.new(), name=ProjectName("API")))
    unit_of_work = InMemoryUnitOfWork(projects, secrets)
    app = create_app(service_name="test-service")

    async def dependency() -> AsyncIterator[CreateSecretUseCase]:
        yield CreateSecretUseCase(unit_of_work)

    app.dependency_overrides[get_create_secret_use_case] = dependency
    return app, project


async def post_secret(app: FastAPI, project_id: str, payload: dict[str, str | None]) -> Response:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        return await client.post(f"/v1/projects/{project_id}/secrets", json=payload)


def test_create_secret_endpoint_returns_created_secret_metadata() -> None:
    async def run() -> None:
        app, project = await build_app_with_project()

        response = await post_secret(
            app,
            str(project.id),
            {"key": "OPENAI_API_KEY", "description": "OpenAI API key metadata."},
        )

        assert response.status_code == 201
        assert response.json()["project_id"] == str(project.id)
        assert response.json()["key"] == "OPENAI_API_KEY"
        assert response.json()["description"] == "OpenAI API key metadata."
        assert isinstance(response.json()["id"], str)

    anyio.run(run)


def test_create_secret_endpoint_returns_bad_request_for_invalid_project_id() -> None:
    async def run() -> None:
        app, _project = await build_app_with_project()

        response = await post_secret(app, "not-a-uuid", {"key": "OPENAI_API_KEY"})

        assert response.status_code == 400
        assert response.json() == {"detail": "Project id must be a valid UUID."}

    anyio.run(run)


def test_create_secret_endpoint_returns_bad_request_for_invalid_key() -> None:
    async def run() -> None:
        app, project = await build_app_with_project()

        response = await post_secret(app, str(project.id), {"key": "openai-api-key"})

        assert response.status_code == 400
        assert response.json() == {
            "detail": "Secret key must contain only A-Z, 0-9 and underscore characters."
        }

    anyio.run(run)


def test_create_secret_endpoint_returns_not_found_for_missing_project() -> None:
    async def run() -> None:
        app, _project = await build_app_with_project()

        response = await post_secret(app, str(ProjectId.new()), {"key": "OPENAI_API_KEY"})

        assert response.status_code == 404
        assert response.json() == {"detail": "Project not found."}

    anyio.run(run)


def test_create_secret_endpoint_returns_conflict_for_duplicate_key_in_project() -> None:
    async def run() -> None:
        app, project = await build_app_with_project()
        first_response = await post_secret(app, str(project.id), {"key": "OPENAI_API_KEY"})

        second_response = await post_secret(app, str(project.id), {"key": "OPENAI_API_KEY"})

        assert first_response.status_code == 201
        assert second_response.status_code == 409
        assert second_response.json() == {
            "detail": "A secret with this key already exists in this project."
        }

    anyio.run(run)

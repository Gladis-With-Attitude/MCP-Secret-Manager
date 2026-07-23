from __future__ import annotations

from collections.abc import AsyncIterator, Sequence
from types import TracebackType
from typing import Self

import anyio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient, Response

from application.project.use_cases import GetProjectUseCase
from application.rbac.dto import RequirePermission
from application.rbac.exceptions import AuthorizationDeniedError
from application.secret.use_cases import (
    ArchiveSecretUseCase,
    CreateSecretUseCase,
    GetSecretUseCase,
    ListSecretsUseCase,
    UpdateSecretUseCase,
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
from presentation.rest.app import create_app
from presentation.rest.authentication import AuthenticatedIdentity, get_authenticated_identity
from presentation.rest.dependencies import (
    get_archive_secret_use_case,
    get_authorize_use_case,
    get_create_secret_use_case,
    get_list_secrets_use_case,
    get_project_use_case,
    get_secret_use_case,
    get_update_secret_use_case,
)


class InMemoryVaultRepository:
    async def create(self, _vault: Vault) -> Vault:
        raise VaultRepositoryConflictError("Vault repository is not used in Secret REST tests.")

    async def get(self, _vault_id: VaultId) -> Vault | None:
        return None

    async def update(self, _vault: Vault) -> Vault:
        raise VaultRepositoryConflictError("Vault repository is not used in Secret REST tests.")

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
        secrets = tuple(
            secret for secret in self._secrets.values() if secret.project_id == project_id
        )
        if status == "archived":
            secrets = tuple(secret for secret in secrets if secret.archived)
        elif status == "active" or not include_archived:
            secrets = tuple(secret for secret in secrets if not secret.archived)
        if secret_type is not None:
            secrets = tuple(secret for secret in secrets if secret.type.value == secret_type)
        if search is not None:
            normalized_search = search.strip().upper()
            secrets = tuple(
                secret
                for secret in secrets
                if normalized_search in secret.key.value
                or (
                    secret.description.value is not None
                    and normalized_search in secret.description.value.upper()
                )
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
                limit=1000,
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
    async def create(self, _secret_version: SecretVersion) -> SecretVersion:
        raise SecretVersionRepositoryConflictError(
            "SecretVersion repository is not used in Secret REST tests."
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
            "SecretVersion repository is not used in Secret REST tests."
        )


class InMemoryUnitOfWork:
    def __init__(self, projects: ProjectRepository, secrets: SecretRepository) -> None:
        self._vaults = InMemoryVaultRepository()
        self._projects = projects
        self._secrets = secrets
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


class FakeAuthorizeUseCase:
    def __init__(self, *, allowed: bool = True) -> None:
        self.allowed = allowed
        self.requests: list[RequirePermission] = []

    async def execute(self, request: RequirePermission) -> None:
        self.requests.append(request)
        if not self.allowed:
            raise AuthorizationDeniedError("Permission denied.")


async def build_app_with_project(
    *,
    authorize_use_case: FakeAuthorizeUseCase | None = None,
) -> tuple[FastAPI, Project]:
    projects = InMemoryProjectRepository()
    secrets = InMemorySecretRepository()
    project = await projects.create(Project.create(vault_id=VaultId.new(), name=ProjectName("API")))
    unit_of_work = InMemoryUnitOfWork(projects, secrets)
    app = create_app(service_name="test-service")
    resolved_authorize_use_case = authorize_use_case or FakeAuthorizeUseCase()
    app.state.authorize_use_case = resolved_authorize_use_case

    async def dependency() -> AsyncIterator[CreateSecretUseCase]:
        yield CreateSecretUseCase(unit_of_work)

    async def list_dependency() -> AsyncIterator[ListSecretsUseCase]:
        yield ListSecretsUseCase(unit_of_work)

    async def get_dependency() -> AsyncIterator[GetSecretUseCase]:
        yield GetSecretUseCase(unit_of_work)

    async def get_project_dependency() -> AsyncIterator[GetProjectUseCase]:
        yield GetProjectUseCase(unit_of_work)

    async def update_dependency() -> AsyncIterator[UpdateSecretUseCase]:
        yield UpdateSecretUseCase(unit_of_work)

    async def archive_dependency() -> AsyncIterator[ArchiveSecretUseCase]:
        yield ArchiveSecretUseCase(unit_of_work)

    app.dependency_overrides[get_create_secret_use_case] = dependency
    app.dependency_overrides[get_list_secrets_use_case] = list_dependency
    app.dependency_overrides[get_secret_use_case] = get_dependency
    app.dependency_overrides[get_project_use_case] = get_project_dependency
    app.dependency_overrides[get_update_secret_use_case] = update_dependency
    app.dependency_overrides[get_archive_secret_use_case] = archive_dependency
    app.dependency_overrides[get_authenticated_identity] = lambda: AuthenticatedIdentity(
        id=str(VaultId.new()),
        type="user",
        api_key_id=str(VaultId.new()),
    )
    app.dependency_overrides[get_authorize_use_case] = lambda: resolved_authorize_use_case
    return app, project


async def post_secret(app: FastAPI, project_id: str, payload: dict[str, str | None]) -> Response:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        return await client.post(f"/v1/projects/{project_id}/secrets", json=payload)


async def get_project_secrets(app: FastAPI, project_id: str, query: str = "") -> Response:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        return await client.get(f"/v1/projects/{project_id}/secrets{query}")


async def get_secret(app: FastAPI, secret_id: str) -> Response:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        return await client.get(f"/v1/secrets/{secret_id}")


async def patch_secret(app: FastAPI, secret_id: str, payload: dict[str, object]) -> Response:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        return await client.patch(f"/v1/secrets/{secret_id}", json=payload)


async def archive_secret(app: FastAPI, secret_id: str) -> Response:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        return await client.post(f"/v1/secrets/{secret_id}/archive")


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


def test_list_secret_endpoint_returns_project_secret_metadata() -> None:
    async def run() -> None:
        app, project = await build_app_with_project()
        await post_secret(
            app,
            str(project.id),
            {
                "key": "OPENAI_API_KEY",
                "description": "OpenAI API key metadata.",
                "type": "api_key",
            },
        )

        response = await get_project_secrets(app, str(project.id), "?q=openai&type=api_key")

        assert response.status_code == 200
        body = response.json()
        assert body["data"][0]["key"] == "OPENAI_API_KEY"
        assert body["data"][0]["type"] == "api_key"
        assert "value" not in body["data"][0]
        assert body["data"][0]["permissions"]["read_value"] is False
        assert body["pagination"]["total"] == 1
        assert body["permissions"]["create"] is True
        assert app.state.authorize_use_case.requests[-1].permission == "secret.read"
        assert app.state.authorize_use_case.requests[-1].scope_type == "project"
        assert app.state.authorize_use_case.requests[-1].scope_id == str(project.id)

    anyio.run(run)


def test_get_update_and_archive_secret_metadata_end_to_end() -> None:
    async def run() -> None:
        app, project = await build_app_with_project()
        created_response = await post_secret(
            app,
            str(project.id),
            {
                "key": "OPENAI_API_KEY",
                "description": "OpenAI API key metadata.",
                "type": "api_key",
            },
        )
        secret_id = created_response.json()["id"]

        get_response = await get_secret(app, secret_id)
        assert get_response.status_code == 200
        assert get_response.json()["key"] == "OPENAI_API_KEY"
        assert app.state.authorize_use_case.requests[-1].permission == "secret.read"
        assert app.state.authorize_use_case.requests[-1].scope_type == "secret"
        assert app.state.authorize_use_case.requests[-1].scope_id == secret_id
        assert app.state.authorize_use_case.requests[-1].parent_project_id == str(project.id)
        assert app.state.authorize_use_case.requests[-1].parent_vault_id == str(project.vault_id)

        update_response = await patch_secret(
            app,
            secret_id,
            {
                "key": "OPENAI_TOKEN",
                "description": "Rotated OpenAI token metadata.",
                "metadata": {"owner": "platform"},
                "tags": ["production", "openai"],
                "type": "token",
            },
        )
        assert update_response.status_code == 200
        assert update_response.json()["key"] == "OPENAI_TOKEN"
        assert update_response.json()["metadata"] == {"owner": "platform"}
        assert update_response.json()["tags"] == ["production", "openai"]
        assert update_response.json()["type"] == "token"
        assert app.state.authorize_use_case.requests[-1].permission == "secret.update"

        archive_response = await archive_secret(app, secret_id)
        assert archive_response.status_code == 200
        assert archive_response.json()["archived"] is True
        assert archive_response.json()["status"] == "archived"
        assert app.state.authorize_use_case.requests[-1].permission == "secret.archive"

        active_list_response = await get_project_secrets(app, str(project.id))
        archived_list_response = await get_project_secrets(app, str(project.id), "?status=archived")
        assert active_list_response.json()["data"] == []
        assert archived_list_response.json()["data"][0]["id"] == secret_id

    anyio.run(run)


def test_secret_endpoint_returns_forbidden_when_permission_is_denied() -> None:
    async def run() -> None:
        app, project = await build_app_with_project(
            authorize_use_case=FakeAuthorizeUseCase(allowed=False)
        )

        response = await get_project_secrets(app, str(project.id))

        assert response.status_code == 403
        assert response.json() == {"detail": "Permission denied."}

    anyio.run(run)


def test_secret_endpoint_requires_identity() -> None:
    async def run() -> None:
        app, project = await build_app_with_project()
        created_response = await post_secret(app, str(project.id), {"key": "OPENAI_API_KEY"})
        app.dependency_overrides.pop(get_authenticated_identity)

        response = await get_secret(app, created_response.json()["id"])

        assert response.status_code == 401
        assert response.json() == {"detail": "Authentication is required."}

    anyio.run(run)


def test_direct_secret_endpoint_rejects_cross_project_access() -> None:
    async def run() -> None:
        app, project = await build_app_with_project()
        created_response = await post_secret(app, str(project.id), {"key": "OPENAI_API_KEY"})
        denied_authorize_use_case = FakeAuthorizeUseCase(allowed=False)
        app.dependency_overrides[get_authorize_use_case] = lambda: denied_authorize_use_case

        response = await get_secret(app, created_response.json()["id"])

        assert response.status_code == 403
        assert response.json() == {"detail": "Permission denied."}
        assert denied_authorize_use_case.requests[-1].parent_project_id == str(project.id)
        assert denied_authorize_use_case.requests[-1].parent_vault_id == str(project.vault_id)

    anyio.run(run)

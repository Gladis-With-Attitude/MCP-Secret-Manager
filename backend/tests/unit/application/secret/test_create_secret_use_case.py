from __future__ import annotations

from collections.abc import Sequence
from types import TracebackType
from typing import Self

import anyio
import pytest

from application.secret.dto import CreateSecretRequest
from application.secret.exceptions import (
    ProjectNotFoundError,
    SecretAlreadyExistsError,
    SecretValidationError,
)
from application.secret.use_cases import CreateSecretUseCase
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


class InMemoryVaultRepository:
    async def create(self, _vault: Vault) -> Vault:
        raise VaultRepositoryConflictError("Vault repository is not used in Secret tests.")

    async def get(self, _vault_id: VaultId) -> Vault | None:
        return None

    async def update(self, _vault: Vault) -> Vault:
        raise VaultRepositoryConflictError("Vault repository is not used in Secret tests.")

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
        self.create_calls = 0

    async def create(self, secret: Secret) -> Secret:
        self.create_calls += 1
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
    async def create(self, _secret_version: SecretVersion) -> SecretVersion:
        raise SecretVersionRepositoryConflictError(
            "SecretVersion repository is not used in Secret tests."
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
    def __init__(self, projects: ProjectRepository, secrets: SecretRepository) -> None:
        self._vaults = InMemoryVaultRepository()
        self._projects = projects
        self._secrets = secrets
        self._secret_versions = InMemorySecretVersionRepository()
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


async def build_unit_of_work_with_project() -> tuple[InMemoryUnitOfWork, Project]:
    projects = InMemoryProjectRepository()
    secrets = InMemorySecretRepository()
    project = await projects.create(Project.create(vault_id=VaultId.new(), name=ProjectName("API")))
    return InMemoryUnitOfWork(projects, secrets), project


def test_create_secret_use_case_creates_secret_in_existing_project() -> None:
    async def run() -> None:
        unit_of_work, project = await build_unit_of_work_with_project()
        secrets = unit_of_work.secrets
        use_case = CreateSecretUseCase(unit_of_work)

        response = await use_case.execute(
            CreateSecretRequest(
                project_id=str(project.id),
                key="OPENAI_API_KEY",
                description="OpenAI API key metadata.",
            )
        )

        assert response.project_id == str(project.id)
        assert response.key == "OPENAI_API_KEY"
        assert response.description == "OpenAI API key metadata."
        assert isinstance(secrets, InMemorySecretRepository)
        assert secrets.create_calls == 1
        assert unit_of_work.committed is True
        assert unit_of_work.rolled_back is False

    anyio.run(run)


def test_create_secret_use_case_accepts_missing_description() -> None:
    async def run() -> None:
        unit_of_work, project = await build_unit_of_work_with_project()
        use_case = CreateSecretUseCase(unit_of_work)

        response = await use_case.execute(
            CreateSecretRequest(project_id=str(project.id), key="DATABASE_URL")
        )

        assert response.description is None

    anyio.run(run)


def test_create_secret_use_case_rejects_invalid_project_id() -> None:
    async def run() -> None:
        unit_of_work, _project = await build_unit_of_work_with_project()
        use_case = CreateSecretUseCase(unit_of_work)

        with pytest.raises(SecretValidationError, match="valid UUID"):
            await use_case.execute(
                CreateSecretRequest(project_id="not-a-uuid", key="OPENAI_API_KEY")
            )

        assert unit_of_work.committed is False
        assert unit_of_work.rolled_back is False

    anyio.run(run)


def test_create_secret_use_case_rejects_invalid_key() -> None:
    async def run() -> None:
        unit_of_work, project = await build_unit_of_work_with_project()
        use_case = CreateSecretUseCase(unit_of_work)

        with pytest.raises(SecretValidationError, match="A-Z"):
            await use_case.execute(CreateSecretRequest(project_id=str(project.id), key="bad-key"))

        assert unit_of_work.committed is False
        assert unit_of_work.rolled_back is False

    anyio.run(run)


def test_create_secret_use_case_rejects_missing_project() -> None:
    async def run() -> None:
        secrets = InMemorySecretRepository()
        unit_of_work = InMemoryUnitOfWork(InMemoryProjectRepository(), secrets)
        use_case = CreateSecretUseCase(unit_of_work)

        with pytest.raises(ProjectNotFoundError, match="not found"):
            await use_case.execute(
                CreateSecretRequest(project_id=str(ProjectId.new()), key="OPENAI_API_KEY")
            )

        assert secrets.create_calls == 0
        assert unit_of_work.committed is False
        assert unit_of_work.rolled_back is True

    anyio.run(run)


def test_create_secret_use_case_rejects_duplicate_key_in_project() -> None:
    async def run() -> None:
        unit_of_work, project = await build_unit_of_work_with_project()
        secrets = unit_of_work.secrets
        use_case = CreateSecretUseCase(unit_of_work)
        await use_case.execute(
            CreateSecretRequest(project_id=str(project.id), key="OPENAI_API_KEY")
        )

        unit_of_work.committed = False
        with pytest.raises(SecretAlreadyExistsError, match="already exists"):
            await use_case.execute(
                CreateSecretRequest(project_id=str(project.id), key="OPENAI_API_KEY")
            )

        assert isinstance(secrets, InMemorySecretRepository)
        assert secrets.create_calls == 1
        assert unit_of_work.committed is False
        assert unit_of_work.rolled_back is True

    anyio.run(run)


def test_create_secret_use_case_allows_same_key_in_different_projects() -> None:
    async def run() -> None:
        projects = InMemoryProjectRepository()
        secrets = InMemorySecretRepository()
        first_project = await projects.create(
            Project.create(vault_id=VaultId.new(), name=ProjectName("API"))
        )
        second_project = await projects.create(
            Project.create(vault_id=VaultId.new(), name=ProjectName("Worker"))
        )
        unit_of_work = InMemoryUnitOfWork(projects, secrets)
        use_case = CreateSecretUseCase(unit_of_work)

        first_response = await use_case.execute(
            CreateSecretRequest(project_id=str(first_project.id), key="OPENAI_API_KEY")
        )
        second_response = await use_case.execute(
            CreateSecretRequest(project_id=str(second_project.id), key="OPENAI_API_KEY")
        )

        assert first_response.key == second_response.key
        assert first_response.project_id != second_response.project_id
        assert secrets.create_calls == 2

    anyio.run(run)


def test_create_secret_use_case_maps_repository_conflict_to_duplicate_error() -> None:
    class ConflictingSecretRepository(InMemorySecretRepository):
        async def exists_in_project(self, _project_id: ProjectId, _key: SecretKey) -> bool:
            return False

        async def create(self, _secret: Secret) -> Secret:
            self.create_calls += 1
            raise SecretRepositoryConflictError("Secret key already exists.")

    async def run() -> None:
        projects = InMemoryProjectRepository()
        project = await projects.create(
            Project.create(vault_id=VaultId.new(), name=ProjectName("API"))
        )
        secrets = ConflictingSecretRepository()
        unit_of_work = InMemoryUnitOfWork(projects, secrets)
        use_case = CreateSecretUseCase(unit_of_work)

        with pytest.raises(SecretAlreadyExistsError, match="already exists"):
            await use_case.execute(
                CreateSecretRequest(project_id=str(project.id), key="OPENAI_API_KEY")
            )

        assert secrets.create_calls == 1
        assert unit_of_work.committed is False
        assert unit_of_work.rolled_back is True

    anyio.run(run)

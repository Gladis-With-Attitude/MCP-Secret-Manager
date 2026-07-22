from __future__ import annotations

from collections.abc import Sequence
from types import TracebackType
from typing import Self

import anyio
import pytest

from application.project.dto import CreateProjectRequest
from application.project.exceptions import (
    ProjectAlreadyExistsError,
    ProjectValidationError,
    VaultNotFoundError,
)
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
            vault.name == name and vault.id != exclude_vault_id
            for vault in self._vaults.values()
        )


class InMemoryProjectRepository:
    def __init__(self) -> None:
        self._projects: dict[ProjectId, Project] = {}
        self.create_calls = 0

    async def create(self, project: Project) -> Project:
        self.create_calls += 1
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


async def build_unit_of_work_with_vault() -> tuple[InMemoryUnitOfWork, Vault]:
    vaults = InMemoryVaultRepository()
    projects = InMemoryProjectRepository()
    vault = await vaults.create(Vault.create(VaultName("Production")))
    return InMemoryUnitOfWork(vaults, projects), vault


def test_create_project_use_case_creates_project_in_existing_vault() -> None:
    async def run() -> None:
        unit_of_work, vault = await build_unit_of_work_with_vault()
        projects = unit_of_work.projects
        use_case = CreateProjectUseCase(unit_of_work)

        response = await use_case.execute(
            CreateProjectRequest(vault_id=str(vault.id), name="  API  ")
        )

        assert response.vault_id == str(vault.id)
        assert response.name == "API"
        assert isinstance(projects, InMemoryProjectRepository)
        assert projects.create_calls == 1
        assert unit_of_work.committed is True
        assert unit_of_work.rolled_back is False

    anyio.run(run)


def test_create_project_use_case_rejects_invalid_vault_id() -> None:
    async def run() -> None:
        unit_of_work, _vault = await build_unit_of_work_with_vault()
        use_case = CreateProjectUseCase(unit_of_work)

        with pytest.raises(ProjectValidationError, match="valid UUID"):
            await use_case.execute(CreateProjectRequest(vault_id="not-a-uuid", name="API"))

        assert unit_of_work.committed is False
        assert unit_of_work.rolled_back is False

    anyio.run(run)


def test_create_project_use_case_rejects_invalid_name() -> None:
    async def run() -> None:
        unit_of_work, vault = await build_unit_of_work_with_vault()
        use_case = CreateProjectUseCase(unit_of_work)

        with pytest.raises(ProjectValidationError, match="at least 3"):
            await use_case.execute(CreateProjectRequest(vault_id=str(vault.id), name="ab"))

        assert unit_of_work.committed is False
        assert unit_of_work.rolled_back is False

    anyio.run(run)


def test_create_project_use_case_rejects_missing_vault() -> None:
    async def run() -> None:
        projects = InMemoryProjectRepository()
        unit_of_work = InMemoryUnitOfWork(InMemoryVaultRepository(), projects)
        use_case = CreateProjectUseCase(unit_of_work)

        with pytest.raises(VaultNotFoundError, match="not found"):
            await use_case.execute(CreateProjectRequest(vault_id=str(VaultId.new()), name="API"))

        assert projects.create_calls == 0
        assert unit_of_work.committed is False
        assert unit_of_work.rolled_back is True

    anyio.run(run)


def test_create_project_use_case_rejects_duplicate_name_in_same_vault() -> None:
    async def run() -> None:
        unit_of_work, vault = await build_unit_of_work_with_vault()
        projects = unit_of_work.projects
        use_case = CreateProjectUseCase(unit_of_work)
        await use_case.execute(CreateProjectRequest(vault_id=str(vault.id), name="API"))

        unit_of_work.committed = False
        with pytest.raises(ProjectAlreadyExistsError, match="already exists"):
            await use_case.execute(CreateProjectRequest(vault_id=str(vault.id), name="API"))

        assert isinstance(projects, InMemoryProjectRepository)
        assert projects.create_calls == 1
        assert unit_of_work.committed is False
        assert unit_of_work.rolled_back is True

    anyio.run(run)


def test_create_project_use_case_allows_same_name_in_different_vaults() -> None:
    async def run() -> None:
        vaults = InMemoryVaultRepository()
        projects = InMemoryProjectRepository()
        first_vault = await vaults.create(Vault.create(VaultName("Production")))
        second_vault = await vaults.create(Vault.create(VaultName("Development")))
        unit_of_work = InMemoryUnitOfWork(vaults, projects)
        use_case = CreateProjectUseCase(unit_of_work)

        first_response = await use_case.execute(
            CreateProjectRequest(vault_id=str(first_vault.id), name="API")
        )
        second_response = await use_case.execute(
            CreateProjectRequest(vault_id=str(second_vault.id), name="API")
        )

        assert first_response.name == second_response.name
        assert first_response.vault_id != second_response.vault_id
        assert projects.create_calls == 2

    anyio.run(run)


def test_create_project_use_case_maps_repository_conflict_to_duplicate_error() -> None:
    class ConflictingProjectRepository(InMemoryProjectRepository):
        async def exists_in_vault(self, _vault_id: VaultId, _name: ProjectName) -> bool:
            return False

        async def create(self, _project: Project) -> Project:
            self.create_calls += 1
            raise ProjectRepositoryConflictError("Project name already exists.")

    async def run() -> None:
        vaults = InMemoryVaultRepository()
        vault = await vaults.create(Vault.create(VaultName("Production")))
        projects = ConflictingProjectRepository()
        unit_of_work = InMemoryUnitOfWork(vaults, projects)
        use_case = CreateProjectUseCase(unit_of_work)

        with pytest.raises(ProjectAlreadyExistsError, match="already exists"):
            await use_case.execute(CreateProjectRequest(vault_id=str(vault.id), name="API"))

        assert projects.create_calls == 1
        assert unit_of_work.committed is False
        assert unit_of_work.rolled_back is True

    anyio.run(run)

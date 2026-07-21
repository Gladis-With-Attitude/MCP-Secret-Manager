from __future__ import annotations

from collections.abc import Sequence
from types import TracebackType
from typing import Self

import anyio
import pytest

from application.unit_of_work import UnitOfWork
from application.vault.dto import CreateVaultRequest
from application.vault.exceptions import VaultAlreadyExistsError, VaultValidationError
from application.vault.use_cases import CreateVaultUseCase
from domain.project.entities import Project
from domain.project.repositories import ProjectRepository, ProjectRepositoryConflictError
from domain.project.value_objects import ProjectId, ProjectName
from domain.vault.entities import Vault
from domain.vault.repositories import VaultRepository, VaultRepositoryConflictError
from domain.vault.value_objects import VaultId, VaultName


class InMemoryVaultRepository:
    def __init__(self) -> None:
        self._vaults: dict[VaultId, Vault] = {}
        self.create_calls = 0

    async def create(self, vault: Vault) -> Vault:
        self.create_calls += 1
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


class InMemoryUnitOfWork:
    def __init__(self, repository: VaultRepository) -> None:
        self._repository = repository
        self._projects = InMemoryProjectRepository()
        self.committed = False
        self.rolled_back = False

    @property
    def vaults(self) -> VaultRepository:
        return self._repository

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
        if exc_type is not None:
            await self.rollback()

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True


async def create_vault(name: str, unit_of_work: UnitOfWork) -> str:
    use_case = CreateVaultUseCase(unit_of_work)

    response = await use_case.execute(CreateVaultRequest(name=name))

    return response.name


def test_create_vault_use_case_creates_and_returns_vault_response() -> None:
    repository = InMemoryVaultRepository()
    unit_of_work = InMemoryUnitOfWork(repository)

    response_name = anyio.run(create_vault, "  Production  ", unit_of_work)

    assert response_name == "Production"
    assert repository.create_calls == 1
    assert unit_of_work.committed is True
    assert unit_of_work.rolled_back is False


def test_create_vault_use_case_rejects_invalid_name() -> None:
    async def run() -> None:
        repository = InMemoryVaultRepository()
        unit_of_work = InMemoryUnitOfWork(repository)
        use_case = CreateVaultUseCase(unit_of_work)

        with pytest.raises(VaultValidationError, match="at least 3"):
            await use_case.execute(CreateVaultRequest(name="ab"))

        assert repository.create_calls == 0
        assert unit_of_work.committed is False
        assert unit_of_work.rolled_back is False

    anyio.run(run)


def test_create_vault_use_case_rejects_duplicate_name_before_creation() -> None:
    async def run() -> None:
        repository = InMemoryVaultRepository()
        unit_of_work = InMemoryUnitOfWork(repository)
        use_case = CreateVaultUseCase(unit_of_work)
        await use_case.execute(CreateVaultRequest(name="Production"))

        unit_of_work.committed = False
        with pytest.raises(VaultAlreadyExistsError, match="already exists"):
            await use_case.execute(CreateVaultRequest(name="Production"))

        assert repository.create_calls == 1
        assert unit_of_work.committed is False
        assert unit_of_work.rolled_back is True

    anyio.run(run)


def test_create_vault_use_case_maps_repository_conflict_to_duplicate_error() -> None:
    class ConflictingVaultRepository(InMemoryVaultRepository):
        async def exists_by_name(self, _name: VaultName) -> bool:
            return False

        async def create(self, _vault: Vault) -> Vault:
            self.create_calls += 1
            raise VaultRepositoryConflictError("Vault name already exists.")

    async def run() -> None:
        repository = ConflictingVaultRepository()
        unit_of_work = InMemoryUnitOfWork(repository)
        use_case = CreateVaultUseCase(unit_of_work)

        with pytest.raises(VaultAlreadyExistsError, match="already exists"):
            await use_case.execute(CreateVaultRequest(name="Production"))

        assert repository.create_calls == 1
        assert unit_of_work.committed is False
        assert unit_of_work.rolled_back is True

    anyio.run(run)

from __future__ import annotations

from collections.abc import Sequence
from types import TracebackType
from typing import Self

import anyio
import pytest

from application.audit.dto import AuditContext
from application.unit_of_work import UnitOfWork
from application.vault.dto import (
    ArchiveVaultRequest,
    CreateVaultRequest,
    GetVaultRequest,
    ListVaultsRequest,
    UpdateVaultRequest,
)
from application.vault.exceptions import (
    VaultAlreadyExistsError,
    VaultArchivedError,
    VaultNotFoundError,
    VaultValidationError,
)
from application.vault.use_cases import (
    ArchiveVaultUseCase,
    CreateVaultUseCase,
    GetVaultUseCase,
    ListVaultsUseCase,
    UpdateVaultUseCase,
)
from domain.audit.entities import AuditEvent
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
        self.create_calls = 0

    async def create(self, vault: Vault) -> Vault:
        self.create_calls += 1
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
        vaults = list(self._vaults.values())
        if status == "archived":
            vaults = [vault for vault in vaults if vault.archived]
        elif status == "locked":
            vaults = [vault for vault in vaults if vault.locked and not vault.archived]
        elif status == "active":
            vaults = [vault for vault in vaults if not vault.archived and not vault.locked]
        elif not include_archived:
            vaults = [vault for vault in vaults if not vault.archived]
        if search:
            normalized_search = search.lower()
            vaults = [
                vault
                for vault in vaults
                if normalized_search in vault.name.value.lower()
                or (
                    vault.description.value is not None
                    and normalized_search in vault.description.value.lower()
                )
            ]
        return tuple(vaults[offset : offset + limit])

    async def count(
        self,
        *,
        include_archived: bool = False,
        search: str | None = None,
        status: str | None = None,
    ) -> int:
        return len(
            await self.list(
                include_archived=include_archived,
                limit=10_000,
                offset=0,
                search=search,
                status=status,
            )
        )

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
        self.committed = False
        self.rolled_back = False

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
        if exc_type is not None:
            await self.rollback()

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        self.rolled_back = True


class RecordingAuditRecorder:
    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    async def record(self, event: AuditEvent) -> None:
        self.events.append(event)


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


def test_create_vault_use_case_persists_optional_description() -> None:
    async def run() -> None:
        repository = InMemoryVaultRepository()
        unit_of_work = InMemoryUnitOfWork(repository)
        use_case = CreateVaultUseCase(unit_of_work)

        response = await use_case.execute(
            CreateVaultRequest(name="Production", description="  Primary boundary  ")
        )

        assert response.description == "Primary boundary"
        assert response.status == "active"
        assert response.archived is False

    anyio.run(run)


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


def test_create_vault_use_case_records_success_audit_event() -> None:
    async def run() -> None:
        repository = InMemoryVaultRepository()
        unit_of_work = InMemoryUnitOfWork(repository)
        audit_recorder = RecordingAuditRecorder()
        use_case = CreateVaultUseCase(unit_of_work, audit_recorder=audit_recorder)

        await use_case.execute(
            CreateVaultRequest(
                name="Production",
                audit_context=AuditContext(actor_id="actor-1", actor_type="user"),
            )
        )

        assert len(audit_recorder.events) == 1
        event = audit_recorder.events[0]
        assert event.action.value == "vault.create"
        assert event.result.value == "SUCCESS"
        assert event.actor_id == "actor-1"
        assert event.resource_id is not None

    anyio.run(run)


def test_create_vault_use_case_records_failure_audit_event() -> None:
    async def run() -> None:
        repository = InMemoryVaultRepository()
        unit_of_work = InMemoryUnitOfWork(repository)
        audit_recorder = RecordingAuditRecorder()
        use_case = CreateVaultUseCase(unit_of_work, audit_recorder=audit_recorder)

        with pytest.raises(VaultValidationError):
            await use_case.execute(
                CreateVaultRequest(
                    name="ab",
                    audit_context=AuditContext(actor_id="actor-1", actor_type="user"),
                )
            )

        assert len(audit_recorder.events) == 1
        event = audit_recorder.events[0]
        assert event.action.value == "vault.create"
        assert event.result.value == "FAILURE"
        assert event.resource_id is None

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


def test_list_vaults_use_case_returns_pagination_and_hides_archived_by_default() -> None:
    async def run() -> None:
        repository = InMemoryVaultRepository()
        unit_of_work = InMemoryUnitOfWork(repository)
        create_use_case = CreateVaultUseCase(unit_of_work)
        archive_use_case = ArchiveVaultUseCase(unit_of_work)
        list_use_case = ListVaultsUseCase(unit_of_work)

        active = await create_use_case.execute(CreateVaultRequest(name="Production"))
        archived = await create_use_case.execute(CreateVaultRequest(name="Legacy"))
        await archive_use_case.execute(ArchiveVaultRequest(vault_id=archived.id))

        response = await list_use_case.execute(ListVaultsRequest(page=1, page_size=10))

        assert [vault.id for vault in response.data] == [active.id]
        assert response.pagination.total == 1
        assert response.permissions.archive is True

    anyio.run(run)


def test_get_vault_use_case_returns_metadata() -> None:
    async def run() -> None:
        repository = InMemoryVaultRepository()
        unit_of_work = InMemoryUnitOfWork(repository)
        created = await CreateVaultUseCase(unit_of_work).execute(
            CreateVaultRequest(name="Production", description="Metadata")
        )

        response = await GetVaultUseCase(unit_of_work).execute(GetVaultRequest(vault_id=created.id))

        assert response.id == created.id
        assert response.description == "Metadata"

    anyio.run(run)


def test_get_vault_use_case_returns_not_found_for_unknown_vault() -> None:
    async def run() -> None:
        repository = InMemoryVaultRepository()
        unit_of_work = InMemoryUnitOfWork(repository)

        with pytest.raises(VaultNotFoundError):
            await GetVaultUseCase(unit_of_work).execute(
                GetVaultRequest(vault_id=str(VaultId.new()))
            )

    anyio.run(run)


def test_update_vault_use_case_updates_metadata_and_rejects_duplicates() -> None:
    async def run() -> None:
        repository = InMemoryVaultRepository()
        unit_of_work = InMemoryUnitOfWork(repository)
        create_use_case = CreateVaultUseCase(unit_of_work)
        update_use_case = UpdateVaultUseCase(unit_of_work)
        first = await create_use_case.execute(CreateVaultRequest(name="Production"))
        await create_use_case.execute(CreateVaultRequest(name="Development"))

        response = await update_use_case.execute(
            UpdateVaultRequest(
                vault_id=first.id,
                name="Platform",
                description="Updated metadata",
            )
        )

        assert response.name == "Platform"
        assert response.description == "Updated metadata"

        with pytest.raises(VaultAlreadyExistsError):
            await update_use_case.execute(UpdateVaultRequest(vault_id=first.id, name="Development"))

    anyio.run(run)


def test_update_vault_use_case_rejects_archived_vault() -> None:
    async def run() -> None:
        repository = InMemoryVaultRepository()
        unit_of_work = InMemoryUnitOfWork(repository)
        created = await CreateVaultUseCase(unit_of_work).execute(CreateVaultRequest(name="Legacy"))
        await ArchiveVaultUseCase(unit_of_work).execute(ArchiveVaultRequest(vault_id=created.id))

        with pytest.raises(VaultArchivedError):
            await UpdateVaultUseCase(unit_of_work).execute(
                UpdateVaultRequest(vault_id=created.id, name="Legacy Updated")
            )

    anyio.run(run)


def test_archive_vault_use_case_marks_vault_archived_idempotently() -> None:
    async def run() -> None:
        repository = InMemoryVaultRepository()
        unit_of_work = InMemoryUnitOfWork(repository)
        created = await CreateVaultUseCase(unit_of_work).execute(CreateVaultRequest(name="Legacy"))
        archive_use_case = ArchiveVaultUseCase(unit_of_work)

        first = await archive_use_case.execute(ArchiveVaultRequest(vault_id=created.id))
        second = await archive_use_case.execute(ArchiveVaultRequest(vault_id=created.id))

        assert first.archived is True
        assert first.status == "archived"
        assert second.archived is True
        assert first.archived_at is not None

    anyio.run(run)


def test_create_vault_use_case_maps_repository_conflict_to_duplicate_error() -> None:
    class ConflictingVaultRepository(InMemoryVaultRepository):
        async def exists_by_name(
            self,
            _name: VaultName,
            *,
            exclude_vault_id: VaultId | None = None,
        ) -> bool:
            _ = exclude_vault_id
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

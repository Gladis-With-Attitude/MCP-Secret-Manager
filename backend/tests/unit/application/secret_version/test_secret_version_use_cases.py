from __future__ import annotations

from collections.abc import Sequence
from types import TracebackType
from typing import Self

import anyio
import pytest

from application.crypto.use_cases import DecryptSecretValueUseCase, EncryptSecretValueUseCase
from application.secret_version.dto import CreateSecretVersionRequest
from application.secret_version.exceptions import (
    SecretNotFoundError,
    SecretVersionConflictError,
    SecretVersionNotFoundError,
    SecretVersionValidationError,
)
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


class InMemoryVaultRepository:
    async def create(self, _vault: Vault) -> Vault:
        raise VaultRepositoryConflictError("Vault repository is not used in SecretVersion tests.")

    async def get(self, _vault_id: VaultId) -> Vault | None:
        return None

    async def update(self, _vault: Vault) -> Vault:
        raise VaultRepositoryConflictError("Vault repository is not used in SecretVersion tests.")

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
            "Project repository is not used in SecretVersion tests."
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
        _ = include_archived, search, status, secret_type
        secrets = tuple(
            secret for secret in self._secrets.values() if secret.project_id == project_id
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
                limit=10_000,
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
    def __init__(self) -> None:
        self._versions: dict[SecretVersionId, SecretVersion] = {}
        self.create_calls = 0
        self.deactivate_calls = 0

    async def create(self, secret_version: SecretVersion) -> SecretVersion:
        self.create_calls += 1
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
        self.deactivate_calls += 1
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


async def build_unit_of_work_with_secret() -> tuple[InMemoryUnitOfWork, Secret]:
    secrets = InMemorySecretRepository()
    secret_versions = InMemorySecretVersionRepository()
    secret = await secrets.create(
        Secret.create(
            project_id=ProjectId.new(),
            key=SecretKey("OPENAI_API_KEY"),
            description=SecretDescription(None),
        )
    )
    return InMemoryUnitOfWork(secrets, secret_versions), secret


def build_create_use_case(unit_of_work: InMemoryUnitOfWork) -> CreateSecretVersionUseCase:
    return CreateSecretVersionUseCase(
        unit_of_work,
        EncryptSecretValueUseCase(FakeCryptoProvider()),
    )


def build_list_use_case(unit_of_work: InMemoryUnitOfWork) -> ListSecretVersionsUseCase:
    return ListSecretVersionsUseCase(
        unit_of_work,
    )


def build_get_active_use_case(
    unit_of_work: InMemoryUnitOfWork,
) -> GetActiveSecretVersionUseCase:
    return GetActiveSecretVersionUseCase(
        unit_of_work,
        DecryptSecretValueUseCase(FakeCryptoProvider()),
    )


def test_create_secret_version_use_case_creates_v1_as_active() -> None:
    async def run() -> None:
        unit_of_work, secret = await build_unit_of_work_with_secret()
        repository = unit_of_work.secret_versions
        use_case = build_create_use_case(unit_of_work)

        response = await use_case.execute(
            CreateSecretVersionRequest(secret_id=str(secret.id), value="plain-value-v1")
        )

        assert response.secret_id == str(secret.id)
        assert not hasattr(response, "value")
        assert response.version == 1
        assert response.active is True
        assert isinstance(repository, InMemorySecretVersionRepository)
        assert repository.create_calls == 1
        assert repository.deactivate_calls == 1
        stored_versions = await repository.list_versions(secret.id)
        assert stored_versions[0].encrypted_value != b"plain-value-v1"
        assert b"plain-value-v1" not in stored_versions[0].encrypted_value
        assert b"plain-value-v1" not in stored_versions[0].encrypted_dek
        assert unit_of_work.committed is True
        assert unit_of_work.rolled_back is False

    anyio.run(run)


def test_create_secret_version_use_case_creates_v2_and_deactivates_v1() -> None:
    async def run() -> None:
        unit_of_work, secret = await build_unit_of_work_with_secret()
        create_use_case = build_create_use_case(unit_of_work)
        await create_use_case.execute(
            CreateSecretVersionRequest(secret_id=str(secret.id), value="plain-value-v1")
        )

        unit_of_work.committed = False
        second_response = await create_use_case.execute(
            CreateSecretVersionRequest(secret_id=str(secret.id), value="plain-value-v2")
        )
        history = await build_list_use_case(unit_of_work).execute(str(secret.id))
        latest = await build_get_active_use_case(unit_of_work).execute(str(secret.id))

        assert second_response.version == 2
        assert second_response.active is True
        assert latest.id == second_response.id
        assert [version.version for version in history] == [1, 2]
        assert [version.active for version in history] == [False, True]
        assert all(not hasattr(version, "value") for version in history)
        assert latest.value == "plain-value-v2"
        assert unit_of_work.committed is True

    anyio.run(run)


def test_create_secret_version_use_case_rejects_invalid_secret_id() -> None:
    async def run() -> None:
        unit_of_work, _secret = await build_unit_of_work_with_secret()
        use_case = build_create_use_case(unit_of_work)

        with pytest.raises(SecretVersionValidationError, match="valid UUID"):
            await use_case.execute(CreateSecretVersionRequest("not-a-uuid", "plain-value"))

        assert unit_of_work.committed is False
        assert unit_of_work.rolled_back is False

    anyio.run(run)


def test_create_secret_version_use_case_rejects_empty_value() -> None:
    async def run() -> None:
        unit_of_work, secret = await build_unit_of_work_with_secret()
        use_case = build_create_use_case(unit_of_work)

        with pytest.raises(SecretVersionValidationError, match="required"):
            await use_case.execute(CreateSecretVersionRequest(secret_id=str(secret.id), value=""))

        assert unit_of_work.committed is False
        assert unit_of_work.rolled_back is False

    anyio.run(run)


def test_create_secret_version_use_case_rejects_missing_secret() -> None:
    async def run() -> None:
        secret_versions = InMemorySecretVersionRepository()
        unit_of_work = InMemoryUnitOfWork(InMemorySecretRepository(), secret_versions)
        use_case = build_create_use_case(unit_of_work)

        with pytest.raises(SecretNotFoundError, match="not found"):
            await use_case.execute(
                CreateSecretVersionRequest(secret_id=str(SecretId.new()), value="plain-value")
            )

        assert secret_versions.create_calls == 0
        assert unit_of_work.committed is False
        assert unit_of_work.rolled_back is True

    anyio.run(run)


def test_get_active_secret_version_use_case_rejects_missing_active_version() -> None:
    async def run() -> None:
        unit_of_work, secret = await build_unit_of_work_with_secret()

        with pytest.raises(SecretVersionNotFoundError, match="Active"):
            await build_get_active_use_case(unit_of_work).execute(str(secret.id))

    anyio.run(run)


def test_create_secret_version_use_case_maps_repository_conflict() -> None:
    class ConflictingSecretVersionRepository(InMemorySecretVersionRepository):
        async def create(self, _secret_version: SecretVersion) -> SecretVersion:
            self.create_calls += 1
            raise SecretVersionRepositoryConflictError("Secret version conflict.")

    async def run() -> None:
        secrets = InMemorySecretRepository()
        secret = await secrets.create(
            Secret.create(
                project_id=ProjectId.new(),
                key=SecretKey("OPENAI_API_KEY"),
                description=SecretDescription(None),
            )
        )
        repository = ConflictingSecretVersionRepository()
        unit_of_work = InMemoryUnitOfWork(secrets, repository)
        use_case = build_create_use_case(unit_of_work)

        with pytest.raises(SecretVersionConflictError, match="conflict"):
            await use_case.execute(
                CreateSecretVersionRequest(secret_id=str(secret.id), value="plain-value")
            )

        assert repository.create_calls == 1
        assert unit_of_work.committed is False
        assert unit_of_work.rolled_back is True

    anyio.run(run)

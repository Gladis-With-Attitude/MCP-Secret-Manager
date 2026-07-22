from __future__ import annotations

from collections.abc import AsyncIterator, Sequence
from types import TracebackType
from typing import Self

import anyio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient, Response

from application.rbac.dto import RequirePermission
from application.rbac.exceptions import AuthorizationDeniedError
from application.vault.use_cases import (
    ArchiveVaultUseCase,
    CreateVaultUseCase,
    GetVaultUseCase,
    ListVaultsUseCase,
    UpdateVaultUseCase,
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
    get_archive_vault_use_case,
    get_authorize_use_case,
    get_create_vault_use_case,
    get_list_vaults_use_case,
    get_update_vault_use_case,
    get_vault_use_case,
)


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
        vaults = list(self._vaults.values())
        if status == "archived":
            vaults = [vault for vault in vaults if vault.archived]
        elif status == "active":
            vaults = [vault for vault in vaults if not vault.archived and not vault.locked]
        elif not include_archived:
            vaults = [vault for vault in vaults if not vault.archived]
        if search:
            vaults = [vault for vault in vaults if search.lower() in vault.name.value.lower()]
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
            vault.name == name and vault.id != exclude_vault_id for vault in self._vaults.values()
        )


class InMemoryProjectRepository:
    async def create(self, _project: Project) -> Project:
        raise ProjectRepositoryConflictError("Project repository is not used in Vault tests.")

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


class FakeAuthorizeUseCase:
    def __init__(self, *, allowed: bool = True) -> None:
        self.allowed = allowed
        self.requests: list[RequirePermission] = []

    async def execute(self, request: RequirePermission) -> None:
        self.requests.append(request)
        if not self.allowed:
            raise AuthorizationDeniedError("Permission denied.")


def build_app(
    repository: InMemoryVaultRepository,
    *,
    authorize_use_case: FakeAuthorizeUseCase | None = None,
) -> FastAPI:
    app = create_app(service_name="test-service")
    unit_of_work = InMemoryUnitOfWork(repository)
    resolved_authorize_use_case = authorize_use_case or FakeAuthorizeUseCase()

    async def create_dependency() -> AsyncIterator[CreateVaultUseCase]:
        yield CreateVaultUseCase(unit_of_work)

    async def list_dependency() -> AsyncIterator[ListVaultsUseCase]:
        yield ListVaultsUseCase(unit_of_work)

    async def get_dependency() -> AsyncIterator[GetVaultUseCase]:
        yield GetVaultUseCase(unit_of_work)

    async def update_dependency() -> AsyncIterator[UpdateVaultUseCase]:
        yield UpdateVaultUseCase(unit_of_work)

    async def archive_dependency() -> AsyncIterator[ArchiveVaultUseCase]:
        yield ArchiveVaultUseCase(unit_of_work)

    async def authorize_dependency() -> AsyncIterator[FakeAuthorizeUseCase]:
        yield resolved_authorize_use_case

    app.dependency_overrides[get_authenticated_identity] = lambda: AuthenticatedIdentity(
        id=str(VaultId.new()),
        type="user",
        api_key_id=str(VaultId.new()),
    )
    app.dependency_overrides[get_authorize_use_case] = authorize_dependency
    app.dependency_overrides[get_create_vault_use_case] = create_dependency
    app.dependency_overrides[get_list_vaults_use_case] = list_dependency
    app.dependency_overrides[get_vault_use_case] = get_dependency
    app.dependency_overrides[get_update_vault_use_case] = update_dependency
    app.dependency_overrides[get_archive_vault_use_case] = archive_dependency
    return app


async def request(
    app: FastAPI,
    method: str,
    path: str,
    payload: dict[str, str] | None = None,
) -> Response:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        return await client.request(method, path, json=payload)


def test_vault_flow_rest_contract() -> None:
    async def run() -> None:
        app = build_app(InMemoryVaultRepository())

        created = await request(
            app,
            "POST",
            "/v1/vaults",
            {"name": "  Production  ", "description": "Primary boundary"},
        )
        assert created.status_code == 201
        created_body = created.json()
        vault_id = created_body["id"]
        assert created_body["name"] == "Production"
        assert created_body["description"] == "Primary boundary"
        assert created_body["status"] == "active"

        listed = await request(app, "GET", "/v1/vaults?page=1&page_size=10")
        assert listed.status_code == 200
        assert listed.json()["data"][0]["id"] == vault_id
        assert listed.json()["pagination"]["total"] == 1

        updated = await request(
            app,
            "PATCH",
            f"/v1/vaults/{vault_id}",
            {"name": "Production Core", "description": "Updated"},
        )
        assert updated.status_code == 200
        assert updated.json()["name"] == "Production Core"

        detail = await request(app, "GET", f"/v1/vaults/{vault_id}")
        assert detail.status_code == 200
        assert detail.json()["name"] == "Production Core"

        archived = await request(app, "POST", f"/v1/vaults/{vault_id}/archive")
        assert archived.status_code == 200
        assert archived.json()["status"] == "archived"

        listed_after_archive = await request(app, "GET", "/v1/vaults")
        assert listed_after_archive.status_code == 200
        assert listed_after_archive.json()["data"] == []

    anyio.run(run)


def test_vault_endpoint_returns_bad_request_for_invalid_name() -> None:
    app = build_app(InMemoryVaultRepository())

    response = anyio.run(request, app, "POST", "/v1/vaults", {"name": "ab"})

    assert response.status_code == 400
    assert response.json() == {"detail": "Vault name must contain at least 3 characters."}


def test_vault_endpoint_returns_conflict_for_duplicate_name() -> None:
    app = build_app(InMemoryVaultRepository())
    first_response = anyio.run(request, app, "POST", "/v1/vaults", {"name": "Production"})

    second_response = anyio.run(request, app, "POST", "/v1/vaults", {"name": "Production"})

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json() == {"detail": "A vault with this name already exists."}


def test_vault_detail_returns_not_found_for_unknown_vault() -> None:
    app = build_app(InMemoryVaultRepository())

    response = anyio.run(request, app, "GET", f"/v1/vaults/{VaultId.new()}")

    assert response.status_code == 404
    assert response.json() == {"detail": "Vault not found."}


def test_vault_endpoint_returns_forbidden_when_permission_is_denied() -> None:
    app = build_app(
        InMemoryVaultRepository(),
        authorize_use_case=FakeAuthorizeUseCase(allowed=False),
    )

    response = anyio.run(request, app, "GET", "/v1/vaults")

    assert response.status_code == 403
    assert response.json() == {"detail": "Forbidden."}

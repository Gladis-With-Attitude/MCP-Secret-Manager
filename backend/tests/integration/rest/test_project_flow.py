from __future__ import annotations

import os
from collections.abc import AsyncIterator, Callable

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from application.audit.use_cases import PersistentAuditRecorder
from application.identity.use_cases import AuthenticateApiKeyUseCase
from application.project.use_cases import (
    ArchiveProjectUseCase,
    CreateProjectUseCase,
    GetProjectUseCase,
    ListProjectsUseCase,
    UpdateProjectUseCase,
)
from application.rbac.use_cases import AuthorizeUseCase, PermissionChecker
from application.vault.use_cases import CreateVaultUseCase
from domain.identity.entities import ApiKey, User
from domain.identity.value_objects import ApiKeyOwnerType, UserDisplayName, UserEmail
from domain.rbac.entities import Permission, Role, RoleAssignment
from domain.rbac.value_objects import PermissionName, RoleName, ScopeType
from infrastructure.identity import Argon2idApiKeyHasher, SecureApiKeySecretGenerator
from infrastructure.persistence import (
    Base,
    SqlAlchemyApiKeyRepository,
    SqlAlchemyPermissionRepository,
    SqlAlchemyRoleAssignmentRepository,
    SqlAlchemyRoleRepository,
    SqlAlchemyUnitOfWork,
    SqlAlchemyUserRepository,
)
from presentation.rest.app import create_app
from presentation.rest.dependencies import (
    get_archive_project_use_case,
    get_authorize_use_case,
    get_create_project_use_case,
    get_create_vault_use_case,
    get_list_projects_use_case,
    get_project_use_case,
    get_update_project_use_case,
)

TEST_SCHEMA = "mcp_secret_manager_project_flow_test"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def database_url() -> str:
    value = os.environ.get("MCP_SECRET_MANAGER_TEST_DATABASE_URL")
    if value is None:
        pytest.skip("MCP_SECRET_MANAGER_TEST_DATABASE_URL is required for PostgreSQL tests.")
    return value


@pytest.fixture
async def session_factory(
    database_url: str,
) -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    admin_engine = create_async_engine(database_url, isolation_level="AUTOCOMMIT")
    async with admin_engine.begin() as connection:
        await connection.execute(text(f'DROP SCHEMA IF EXISTS "{TEST_SCHEMA}" CASCADE'))
        await connection.execute(text(f'CREATE SCHEMA "{TEST_SCHEMA}"'))
    await admin_engine.dispose()

    engine = create_async_engine(
        database_url,
        connect_args={"server_settings": {"search_path": TEST_SCHEMA}},
    )
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    try:
        yield async_sessionmaker(engine, expire_on_commit=False)
    finally:
        await engine.dispose()
        cleanup_engine = create_async_engine(database_url, isolation_level="AUTOCOMMIT")
        async with cleanup_engine.begin() as connection:
            await connection.execute(text(f'DROP SCHEMA IF EXISTS "{TEST_SCHEMA}" CASCADE'))
        await cleanup_engine.dispose()


async def create_authenticated_project_client(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncClient]:
    generator = SecureApiKeySecretGenerator()
    hasher = Argon2idApiKeyHasher()
    raw_api_key = generator.generate()
    key_prefix = generator.extract_prefix(raw_api_key)
    assert key_prefix is not None

    await seed_project_operator(session_factory, raw_api_key, key_prefix, hasher)

    audit_recorder = PersistentAuditRecorder(SqlAlchemyUnitOfWork(session_factory))
    authenticate_api_key_use_case = AuthenticateApiKeyUseCase(
        SqlAlchemyUnitOfWork(session_factory),
        generator,
        hasher,
        audit_recorder=audit_recorder,
    )
    app = create_app(
        service_name="test-service",
        authenticate_api_key_use_case=authenticate_api_key_use_case,
    )

    def use_case_factory(
        use_case: Callable[[SqlAlchemyUnitOfWork], object],
    ) -> Callable[[], object]:
        return lambda: use_case(SqlAlchemyUnitOfWork(session_factory))

    app.dependency_overrides[get_create_vault_use_case] = lambda: CreateVaultUseCase(
        SqlAlchemyUnitOfWork(session_factory),
        audit_recorder=audit_recorder,
    )
    app.dependency_overrides[get_create_project_use_case] = lambda: CreateProjectUseCase(
        SqlAlchemyUnitOfWork(session_factory),
        audit_recorder=audit_recorder,
    )
    app.dependency_overrides[get_list_projects_use_case] = use_case_factory(ListProjectsUseCase)
    app.dependency_overrides[get_project_use_case] = lambda: GetProjectUseCase(
        SqlAlchemyUnitOfWork(session_factory),
        audit_recorder=audit_recorder,
    )
    app.dependency_overrides[get_update_project_use_case] = lambda: UpdateProjectUseCase(
        SqlAlchemyUnitOfWork(session_factory),
        audit_recorder=audit_recorder,
    )
    app.dependency_overrides[get_archive_project_use_case] = lambda: ArchiveProjectUseCase(
        SqlAlchemyUnitOfWork(session_factory),
        audit_recorder=audit_recorder,
    )
    app.dependency_overrides[get_authorize_use_case] = lambda: AuthorizeUseCase(
        PermissionChecker(SqlAlchemyUnitOfWork(session_factory)),
        audit_recorder=audit_recorder,
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        headers={"Authorization": f"Bearer {raw_api_key}"},
    ) as client:
        yield client


async def seed_project_operator(
    session_factory: async_sessionmaker[AsyncSession],
    raw_api_key: str,
    key_prefix: str,
    hasher: Argon2idApiKeyHasher,
) -> None:
    async with session_factory() as session:
        user_repository = SqlAlchemyUserRepository(session)
        permission_repository = SqlAlchemyPermissionRepository(session)
        role_repository = SqlAlchemyRoleRepository(session)
        assignment_repository = SqlAlchemyRoleAssignmentRepository(session)
        api_key_repository = SqlAlchemyApiKeyRepository(session)

        user = await user_repository.create(
            User.create(
                email=UserEmail("project.operator@example.test"),
                display_name=UserDisplayName("Project Operator"),
            )
        )
        role = await role_repository.create(
            Role.create(RoleName("project-operator"), "Project integration test operator.")
        )
        for permission_name in (
            "vault.create",
            "project.create",
            "project.read",
            "project.update",
            "project.archive",
        ):
            permission = await permission_repository.create(
                Permission.create(PermissionName(permission_name), None)
            )
            await role_repository.add_permission(role.id, permission.id)

        await assignment_repository.create(
            RoleAssignment.create(
                identity_id=user.id,
                identity_type=ApiKeyOwnerType.USER,
                scope_type=ScopeType.GLOBAL,
                scope_id=None,
                role_id=role.id,
            )
        )
        await api_key_repository.create(
            ApiKey.create(
                hashed_key=hasher.hash(raw_api_key),
                key_prefix=key_prefix,
                owner_id=user.id,
                owner_type=ApiKeyOwnerType.USER,
                expires_at=None,
            )
        )
        await session.commit()


@pytest.mark.integration
@pytest.mark.anyio
async def test_project_browser_to_postgres_flow(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async for client in create_authenticated_project_client(session_factory):
        created_vault = await client.post(
            "/v1/vaults",
            json={"name": "Production", "description": "Primary boundary"},
        )
        assert created_vault.status_code == 201
        vault_id = created_vault.json()["id"]

        created_project = await client.post(
            f"/v1/vaults/{vault_id}/projects",
            json={"name": "API", "description": "Application services"},
        )
        assert created_project.status_code == 201
        project_id = created_project.json()["id"]

        listed = await client.get(
            f"/v1/vaults/{vault_id}/projects",
            params={"page": 1, "page_size": 20},
        )
        assert listed.status_code == 200
        assert [project["id"] for project in listed.json()["data"]] == [project_id]

        updated = await client.patch(
            f"/v1/projects/{project_id}",
            json={"name": "API Core", "description": "Updated metadata"},
        )
        assert updated.status_code == 200
        assert updated.json()["name"] == "API Core"

        detail = await client.get(f"/v1/projects/{project_id}")
        assert detail.status_code == 200
        assert detail.json()["description"] == "Updated metadata"

        archived = await client.post(f"/v1/projects/{project_id}/archive")
        assert archived.status_code == 200
        assert archived.json()["status"] == "archived"

        listed_after_archive = await client.get(f"/v1/vaults/{vault_id}/projects")
        assert listed_after_archive.status_code == 200
        assert listed_after_archive.json()["data"] == []

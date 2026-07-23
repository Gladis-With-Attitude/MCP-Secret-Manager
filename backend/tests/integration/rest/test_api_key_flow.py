from __future__ import annotations

import os
from collections.abc import AsyncIterator, Callable

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from application.audit.use_cases import PersistentAuditRecorder
from application.identity.use_cases import (
    AuthenticateApiKeyUseCase,
    CreateApiKeyUseCase,
    GetApiKeyUseCase,
    ListApiKeysUseCase,
    RevokeApiKeyUseCase,
    UpdateApiKeyUseCase,
)
from application.rbac.use_cases import AuthorizeUseCase, PermissionChecker
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
    get_api_key_use_case,
    get_authorize_use_case,
    get_create_api_key_use_case,
    get_list_api_keys_use_case,
    get_revoke_api_key_use_case,
    get_update_api_key_use_case,
)

TEST_SCHEMA = "mcp_secret_manager_api_key_flow_test"


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


async def create_authenticated_api_key_client(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[tuple[AsyncClient, str]]:
    generator = SecureApiKeySecretGenerator()
    hasher = Argon2idApiKeyHasher()
    raw_api_key = generator.generate()
    key_prefix = generator.extract_prefix(raw_api_key)
    assert key_prefix is not None
    owner_id = await seed_api_key_operator(session_factory, raw_api_key, key_prefix, hasher)

    audit_recorder = PersistentAuditRecorder(SqlAlchemyUnitOfWork(session_factory))
    app = create_app(
        service_name="test-service",
        authenticate_api_key_use_case=AuthenticateApiKeyUseCase(
            SqlAlchemyUnitOfWork(session_factory),
            generator,
            hasher,
            audit_recorder=audit_recorder,
        ),
    )

    def use_case_factory(
        use_case: Callable[[SqlAlchemyUnitOfWork], object],
    ) -> Callable[[], object]:
        return lambda: use_case(SqlAlchemyUnitOfWork(session_factory))

    app.dependency_overrides[get_create_api_key_use_case] = lambda: CreateApiKeyUseCase(
        SqlAlchemyUnitOfWork(session_factory),
        generator,
        hasher,
        audit_recorder=audit_recorder,
    )
    app.dependency_overrides[get_list_api_keys_use_case] = use_case_factory(ListApiKeysUseCase)
    app.dependency_overrides[get_api_key_use_case] = use_case_factory(GetApiKeyUseCase)
    app.dependency_overrides[get_update_api_key_use_case] = lambda: UpdateApiKeyUseCase(
        SqlAlchemyUnitOfWork(session_factory),
        audit_recorder=audit_recorder,
    )
    app.dependency_overrides[get_revoke_api_key_use_case] = lambda: RevokeApiKeyUseCase(
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
        yield client, str(owner_id)


async def seed_api_key_operator(
    session_factory: async_sessionmaker[AsyncSession],
    raw_api_key: str,
    key_prefix: str,
    hasher: Argon2idApiKeyHasher,
) -> object:
    async with session_factory() as session:
        user_repository = SqlAlchemyUserRepository(session)
        permission_repository = SqlAlchemyPermissionRepository(session)
        role_repository = SqlAlchemyRoleRepository(session)
        assignment_repository = SqlAlchemyRoleAssignmentRepository(session)
        api_key_repository = SqlAlchemyApiKeyRepository(session)

        user = await user_repository.create(
            User.create(
                email=UserEmail("apikey.operator@example.test"),
                display_name=UserDisplayName("API Key Operator"),
            )
        )
        role = await role_repository.create(
            Role.create(RoleName("api-key-operator"), "API key integration test operator.")
        )
        for permission_name in (
            "apikey.create",
            "apikey.read",
            "apikey.update",
            "apikey.revoke",
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
                name="bootstrap admin key",
                granted_permissions=("apikey.create", "apikey.read"),
                scopes=("global",),
            )
        )
        await session.commit()
        return user.id


@pytest.mark.integration
@pytest.mark.anyio
async def test_api_key_browser_to_postgres_flow(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async for client, owner_id in create_authenticated_api_key_client(session_factory):
        created = await client.post(
            "/v1/tokens",
            json={
                "name": "agent",
                "description": "Production agent",
                "owner_id": owner_id,
                "owner_type": "user",
                "permissions": ["secret.read"],
                "scopes": ["global"],
            },
        )
        assert created.status_code == 201
        created_payload = created.json()
        api_key_id = created_payload["id"]
        assert created_payload["api_key"].startswith(created_payload["key_prefix"])
        assert created_payload["token"] == created_payload["api_key"]
        assert created_payload["granted_permissions"] == ["secret.read"]
        assert "hashed_key" not in created_payload

        listed = await client.get("/v1/tokens", params={"search": "agent", "status": "active"})
        assert listed.status_code == 200
        listed_payload = listed.json()
        assert [item["id"] for item in listed_payload["data"]] == [api_key_id]
        assert "api_key" not in listed_payload["data"][0]

        detail = await client.get(f"/v1/tokens/{api_key_id}")
        assert detail.status_code == 200
        assert detail.json()["name"] == "agent"
        assert "api_key" not in detail.json()

        updated = await client.patch(
            f"/v1/tokens/{api_key_id}",
            json={
                "name": "agent rotated",
                "description": "Updated owner note",
                "permissions": ["secret.read", "secret.rotate"],
                "scopes": ["global"],
            },
        )
        assert updated.status_code == 200
        assert updated.json()["name"] == "agent rotated"
        assert updated.json()["granted_permissions"] == ["secret.read", "secret.rotate"]

        revoked = await client.post(f"/v1/tokens/{api_key_id}/revoke")
        assert revoked.status_code == 200
        assert revoked.json()["status"] == "revoked"
        assert revoked.json()["revoked_at"] is not None

        revoked_list = await client.get("/v1/tokens", params={"status": "revoked"})
        assert revoked_list.status_code == 200
        assert [item["id"] for item in revoked_list.json()["data"]] == [api_key_id]

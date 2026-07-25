from __future__ import annotations

import os
from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from application.audit.use_cases import (
    GetAuditEventUseCase,
    ListAuditEventsUseCase,
    PersistentAuditRecorder,
)
from application.identity.use_cases import AuthenticateApiKeyUseCase
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
    get_audit_event_use_case,
    get_authorize_use_case,
    get_create_vault_use_case,
    get_list_audit_events_use_case,
)

TEST_SCHEMA = "mcp_secret_manager_audit_flow_test"


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


async def create_authenticated_audit_client(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncClient]:
    generator = SecureApiKeySecretGenerator()
    hasher = Argon2idApiKeyHasher()
    raw_api_key = generator.generate()
    key_prefix = generator.extract_prefix(raw_api_key)
    assert key_prefix is not None

    await seed_audit_operator(session_factory, raw_api_key, key_prefix, hasher)

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
    app.dependency_overrides[get_create_vault_use_case] = lambda: CreateVaultUseCase(
        SqlAlchemyUnitOfWork(session_factory),
        audit_recorder=audit_recorder,
    )
    app.dependency_overrides[get_list_audit_events_use_case] = lambda: ListAuditEventsUseCase(
        SqlAlchemyUnitOfWork(session_factory)
    )
    app.dependency_overrides[get_audit_event_use_case] = lambda: GetAuditEventUseCase(
        SqlAlchemyUnitOfWork(session_factory)
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


async def seed_audit_operator(
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
                email=UserEmail("audit.operator@example.test"),
                display_name=UserDisplayName("Audit Operator"),
            )
        )
        role = await role_repository.create(
            Role.create(RoleName("audit-operator"), "Audit integration test operator.")
        )
        for permission_name in ("audit.read", "vault.create"):
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
async def test_audit_browser_to_postgres_flow(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async for client in create_authenticated_audit_client(session_factory):
        created = await client.post(
            "/v1/vaults",
            headers={"X-Request-ID": "req-audit-e2e"},
            json={"name": "Production Audit", "description": "Audited boundary"},
        )
        assert created.status_code == 201
        vault_id = created.json()["id"]

        listed = await client.get(
            "/v1/audit/events",
            params={"action": "vault.create", "q": "Production Audit", "limit": 25},
        )
        assert listed.status_code == 200
        events = listed.json()
        assert len(events) == 1
        assert events[0]["resource_id"] == vault_id
        assert events[0]["metadata"] == {"name": "Production Audit", "protocol": "rest"}
        assert events[0]["request_id"] == "req-audit-e2e"

        detail = await client.get(f"/v1/audit/events/{events[0]['id']}")
        assert detail.status_code == 200
        assert detail.json()["id"] == events[0]["id"]
        assert detail.json()["action"] == "vault.create"

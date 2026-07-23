from __future__ import annotations

import os
from collections.abc import AsyncIterator, Callable

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from application.audit.use_cases import PersistentAuditRecorder
from application.identity.use_cases import AuthenticateApiKeyUseCase
from application.rbac.use_cases import (
    AssignActorRoleUseCase,
    AuthorizeUseCase,
    CreateRoleUseCase,
    GetRoleUseCase,
    ListActorRolesUseCase,
    ListPermissionsUseCase,
    ListRolesUseCase,
    PermissionChecker,
    RevokeActorRoleUseCase,
    UpdateRoleUseCase,
)
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
    get_assign_actor_role_use_case,
    get_authorize_use_case,
    get_create_role_use_case,
    get_list_actor_roles_use_case,
    get_list_permissions_use_case,
    get_list_roles_use_case,
    get_revoke_actor_role_use_case,
    get_role_use_case,
    get_update_role_use_case,
)

TEST_SCHEMA = "mcp_secret_manager_rbac_flow_test"


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


async def create_authenticated_rbac_client(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[tuple[AsyncClient, str]]:
    generator = SecureApiKeySecretGenerator()
    hasher = Argon2idApiKeyHasher()
    raw_api_key = generator.generate()
    key_prefix = generator.extract_prefix(raw_api_key)
    assert key_prefix is not None
    actor_id = await seed_rbac_operator(session_factory, raw_api_key, key_prefix, hasher)

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

    app.dependency_overrides[get_list_permissions_use_case] = use_case_factory(
        ListPermissionsUseCase
    )
    app.dependency_overrides[get_list_roles_use_case] = use_case_factory(ListRolesUseCase)
    app.dependency_overrides[get_role_use_case] = lambda: GetRoleUseCase(
        SqlAlchemyUnitOfWork(session_factory),
        audit_recorder=audit_recorder,
    )
    app.dependency_overrides[get_create_role_use_case] = lambda: CreateRoleUseCase(
        SqlAlchemyUnitOfWork(session_factory),
        audit_recorder=audit_recorder,
    )
    app.dependency_overrides[get_update_role_use_case] = lambda: UpdateRoleUseCase(
        SqlAlchemyUnitOfWork(session_factory),
        audit_recorder=audit_recorder,
    )
    app.dependency_overrides[get_list_actor_roles_use_case] = use_case_factory(
        ListActorRolesUseCase
    )
    app.dependency_overrides[get_assign_actor_role_use_case] = lambda: AssignActorRoleUseCase(
        SqlAlchemyUnitOfWork(session_factory),
        audit_recorder=audit_recorder,
    )
    app.dependency_overrides[get_revoke_actor_role_use_case] = lambda: RevokeActorRoleUseCase(
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
        yield client, str(actor_id)


async def seed_rbac_operator(
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

        operator = await user_repository.create(
            User.create(
                email=UserEmail("rbac.operator@example.test"),
                display_name=UserDisplayName("RBAC Operator"),
            )
        )
        await user_repository.create(
            User.create(
                email=UserEmail("rbac.assignee@example.test"),
                display_name=UserDisplayName("RBAC Assignee"),
            )
        )
        role = await role_repository.create(
            Role.create(RoleName("rbac-operator"), "RBAC integration test operator.")
        )
        for permission_name in (
            "role.read",
            "role.create",
            "role.update",
            "role.assign",
            "role.revoke",
            "secret.read",
        ):
            permission = await permission_repository.create(
                Permission.create(PermissionName(permission_name), None)
            )
            await role_repository.add_permission(role.id, permission.id)

        await assignment_repository.create(
            RoleAssignment.create(
                identity_id=operator.id,
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
                owner_id=operator.id,
                owner_type=ApiKeyOwnerType.USER,
                expires_at=None,
                name="bootstrap rbac key",
                granted_permissions=("role.read", "role.create", "role.update"),
                scopes=("global",),
            )
        )
        await session.commit()
        return operator.id


@pytest.mark.integration
@pytest.mark.anyio
async def test_rbac_browser_to_postgres_flow(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async for client, actor_id in create_authenticated_rbac_client(session_factory):
        permissions = await client.get("/v1/permissions")
        assert permissions.status_code == 200
        permission_payload = permissions.json()["data"]
        secret_read_id = next(
            permission["id"]
            for permission in permission_payload
            if permission["name"] == "secret.read"
        )

        created = await client.post(
            "/v1/roles",
            json={
                "name": "custom-reader",
                "description": "Read project secrets.",
                "permission_ids": [secret_read_id],
            },
        )
        assert created.status_code == 201
        created_payload = created.json()
        role_id = created_payload["id"]
        assert created_payload["kind"] == "custom"
        assert created_payload["permission_ids"] == [secret_read_id]

        updated = await client.patch(
            f"/v1/roles/{role_id}",
            json={
                "name": "custom-secret-reader",
                "description": "Updated read role.",
                "permission_ids": [secret_read_id],
            },
        )
        assert updated.status_code == 200
        assert updated.json()["name"] == "custom-secret-reader"

        listed = await client.get("/v1/roles", params={"q": "secret-reader", "kind": "custom"})
        assert listed.status_code == 200
        assert [role["id"] for role in listed.json()["data"]] == [role_id]
        assert listed.json()["permissions"]["create"] is True

        detail = await client.get(f"/v1/roles/{role_id}")
        assert detail.status_code == 200
        assert detail.json()["permissions"][0]["name"] == "secret.read"

        assigned = await client.post(f"/v1/actors/{actor_id}/roles/{role_id}")
        assert assigned.status_code == 201
        assert assigned.json()["actor_id"] == actor_id
        assert assigned.json()["role_id"] == role_id

        assignments = await client.get(f"/v1/actors/{actor_id}/roles")
        assert assignments.status_code == 200
        assert role_id in {assignment["role_id"] for assignment in assignments.json()["data"]}
        assert assignments.json()["permissions"]["revoke"] is True

        revoked = await client.delete(f"/v1/actors/{actor_id}/roles/{role_id}")
        assert revoked.status_code == 200
        assert revoked.json()["status"] == "revoked"

        remaining = await client.get(f"/v1/actors/{actor_id}/roles")
        assert remaining.status_code == 200
        assert role_id not in {assignment["role_id"] for assignment in remaining.json()["data"]}

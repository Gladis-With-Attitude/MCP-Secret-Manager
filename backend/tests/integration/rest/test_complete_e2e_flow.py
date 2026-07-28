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
from application.crypto.use_cases import DecryptSecretValueUseCase, EncryptSecretValueUseCase
from application.identity.use_cases import (
    AuthenticateApiKeyUseCase,
    AuthenticateSessionUseCase,
    CreateApiKeyUseCase,
    CreateSessionUseCase,
    GetApiKeyUseCase,
    GetCurrentSessionUseCase,
    ListApiKeysUseCase,
    RevokeApiKeyUseCase,
    RevokeCurrentSessionUseCase,
)
from application.project.use_cases import (
    CreateProjectUseCase,
    GetProjectUseCase,
    ListProjectsUseCase,
)
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
)
from application.secret.use_cases import CreateSecretUseCase, GetSecretUseCase, ListSecretsUseCase
from application.secret_version.use_cases import (
    CreateSecretVersionUseCase,
    GetActiveSecretVersionUseCase,
    GetSecretVersionMetadataUseCase,
    ListSecretVersionsUseCase,
)
from application.vault.use_cases import CreateVaultUseCase, GetVaultUseCase, ListVaultsUseCase
from domain.identity.entities import ApiKey, User
from domain.identity.value_objects import ApiKeyOwnerType, UserDisplayName, UserEmail
from domain.rbac.entities import Permission, Role, RoleAssignment
from domain.rbac.permissions import DEFAULT_PERMISSIONS
from domain.rbac.value_objects import PermissionName, RoleName, ScopeType
from infrastructure.crypto import AesGcmCryptoProvider
from infrastructure.identity import (
    Argon2idApiKeyHasher,
    SecureApiKeySecretGenerator,
    SecureSessionTokenGenerator,
)
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
    get_active_secret_version_use_case,
    get_api_key_use_case,
    get_assign_actor_role_use_case,
    get_audit_event_use_case,
    get_authorize_use_case,
    get_create_api_key_use_case,
    get_create_project_use_case,
    get_create_role_use_case,
    get_create_secret_use_case,
    get_create_secret_version_use_case,
    get_create_session_use_case,
    get_create_vault_use_case,
    get_current_session_use_case,
    get_list_actor_roles_use_case,
    get_list_api_keys_use_case,
    get_list_audit_events_use_case,
    get_list_permissions_use_case,
    get_list_projects_use_case,
    get_list_roles_use_case,
    get_list_secret_versions_use_case,
    get_list_secrets_use_case,
    get_list_vaults_use_case,
    get_project_use_case,
    get_revoke_actor_role_use_case,
    get_revoke_api_key_use_case,
    get_revoke_current_session_use_case,
    get_role_use_case,
    get_secret_use_case,
    get_secret_version_metadata_use_case,
    get_vault_use_case,
)

TEST_SCHEMA = "mcp_secret_manager_complete_e2e_test"


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


async def create_complete_e2e_client(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[tuple[AsyncClient, str, str]]:
    api_key_generator = SecureApiKeySecretGenerator()
    api_key_hasher = Argon2idApiKeyHasher()
    session_token_generator = SecureSessionTokenGenerator()
    session_token_hasher = Argon2idApiKeyHasher()
    raw_api_key = api_key_generator.generate()
    key_prefix = api_key_generator.extract_prefix(raw_api_key)
    assert key_prefix is not None
    user_id = await seed_complete_e2e_operator(
        session_factory,
        raw_api_key,
        key_prefix,
        api_key_hasher,
    )

    audit_recorder = PersistentAuditRecorder(SqlAlchemyUnitOfWork(session_factory))
    crypto_provider = AesGcmCryptoProvider.from_base64_master_key(
        os.environ["MCP_SECRET_MANAGER_MASTER_KEY_BASE64"],
        key_version=1,
    )
    app = create_app(
        service_name="test-service",
        authenticate_api_key_use_case=AuthenticateApiKeyUseCase(
            SqlAlchemyUnitOfWork(session_factory),
            api_key_generator,
            api_key_hasher,
            audit_recorder=audit_recorder,
        ),
        authenticate_session_use_case=AuthenticateSessionUseCase(
            SqlAlchemyUnitOfWork(session_factory),
            session_token_generator,
            session_token_hasher,
        ),
    )

    app.dependency_overrides[get_create_session_use_case] = lambda: CreateSessionUseCase(
        SqlAlchemyUnitOfWork(session_factory),
        api_key_generator,
        api_key_hasher,
        session_token_generator,
        session_token_hasher,
        audit_recorder=audit_recorder,
    )
    app.dependency_overrides[get_current_session_use_case] = lambda: GetCurrentSessionUseCase(
        SqlAlchemyUnitOfWork(session_factory)
    )
    app.dependency_overrides[get_revoke_current_session_use_case] = lambda: (
        RevokeCurrentSessionUseCase(
            SqlAlchemyUnitOfWork(session_factory),
            audit_recorder=audit_recorder,
        )
    )
    app.dependency_overrides[get_authorize_use_case] = lambda: AuthorizeUseCase(
        PermissionChecker(SqlAlchemyUnitOfWork(session_factory)),
        audit_recorder=audit_recorder,
    )
    app.dependency_overrides[get_create_vault_use_case] = lambda: CreateVaultUseCase(
        SqlAlchemyUnitOfWork(session_factory),
        audit_recorder=audit_recorder,
    )
    app.dependency_overrides[get_list_vaults_use_case] = lambda: ListVaultsUseCase(
        SqlAlchemyUnitOfWork(session_factory)
    )
    app.dependency_overrides[get_vault_use_case] = lambda: GetVaultUseCase(
        SqlAlchemyUnitOfWork(session_factory),
        audit_recorder=audit_recorder,
    )
    app.dependency_overrides[get_create_project_use_case] = lambda: CreateProjectUseCase(
        SqlAlchemyUnitOfWork(session_factory),
        audit_recorder=audit_recorder,
    )
    app.dependency_overrides[get_list_projects_use_case] = lambda: ListProjectsUseCase(
        SqlAlchemyUnitOfWork(session_factory)
    )
    app.dependency_overrides[get_project_use_case] = lambda: GetProjectUseCase(
        SqlAlchemyUnitOfWork(session_factory),
        audit_recorder=audit_recorder,
    )
    app.dependency_overrides[get_create_secret_use_case] = lambda: CreateSecretUseCase(
        SqlAlchemyUnitOfWork(session_factory),
        audit_recorder=audit_recorder,
    )
    app.dependency_overrides[get_list_secrets_use_case] = lambda: ListSecretsUseCase(
        SqlAlchemyUnitOfWork(session_factory),
        audit_recorder=audit_recorder,
    )
    app.dependency_overrides[get_secret_use_case] = lambda: GetSecretUseCase(
        SqlAlchemyUnitOfWork(session_factory),
        audit_recorder=audit_recorder,
    )
    app.dependency_overrides[get_create_secret_version_use_case] = lambda: (
        CreateSecretVersionUseCase(
            SqlAlchemyUnitOfWork(session_factory),
            EncryptSecretValueUseCase(crypto_provider),
            audit_recorder=audit_recorder,
        )
    )
    app.dependency_overrides[get_list_secret_versions_use_case] = lambda: ListSecretVersionsUseCase(
        SqlAlchemyUnitOfWork(session_factory),
        audit_recorder=audit_recorder,
    )
    app.dependency_overrides[get_secret_version_metadata_use_case] = lambda: (
        GetSecretVersionMetadataUseCase(
            SqlAlchemyUnitOfWork(session_factory),
            audit_recorder=audit_recorder,
        )
    )
    app.dependency_overrides[get_active_secret_version_use_case] = lambda: (
        GetActiveSecretVersionUseCase(
            SqlAlchemyUnitOfWork(session_factory),
            DecryptSecretValueUseCase(crypto_provider),
            audit_recorder=audit_recorder,
        )
    )
    app.dependency_overrides[get_create_api_key_use_case] = lambda: CreateApiKeyUseCase(
        SqlAlchemyUnitOfWork(session_factory),
        api_key_generator,
        api_key_hasher,
        audit_recorder=audit_recorder,
    )
    app.dependency_overrides[get_list_api_keys_use_case] = lambda: ListApiKeysUseCase(
        SqlAlchemyUnitOfWork(session_factory)
    )
    app.dependency_overrides[get_api_key_use_case] = lambda: GetApiKeyUseCase(
        SqlAlchemyUnitOfWork(session_factory)
    )
    app.dependency_overrides[get_revoke_api_key_use_case] = lambda: RevokeApiKeyUseCase(
        SqlAlchemyUnitOfWork(session_factory),
        audit_recorder=audit_recorder,
    )
    app.dependency_overrides[get_list_permissions_use_case] = lambda: ListPermissionsUseCase(
        SqlAlchemyUnitOfWork(session_factory)
    )
    app.dependency_overrides[get_list_roles_use_case] = lambda: ListRolesUseCase(
        SqlAlchemyUnitOfWork(session_factory)
    )
    app.dependency_overrides[get_role_use_case] = lambda: GetRoleUseCase(
        SqlAlchemyUnitOfWork(session_factory),
        audit_recorder=audit_recorder,
    )
    app.dependency_overrides[get_create_role_use_case] = lambda: CreateRoleUseCase(
        SqlAlchemyUnitOfWork(session_factory),
        audit_recorder=audit_recorder,
    )
    app.dependency_overrides[get_list_actor_roles_use_case] = lambda: ListActorRolesUseCase(
        SqlAlchemyUnitOfWork(session_factory)
    )
    app.dependency_overrides[get_assign_actor_role_use_case] = lambda: AssignActorRoleUseCase(
        SqlAlchemyUnitOfWork(session_factory),
        audit_recorder=audit_recorder,
    )
    app.dependency_overrides[get_revoke_actor_role_use_case] = lambda: RevokeActorRoleUseCase(
        SqlAlchemyUnitOfWork(session_factory),
        audit_recorder=audit_recorder,
    )
    app.dependency_overrides[get_list_audit_events_use_case] = lambda: ListAuditEventsUseCase(
        SqlAlchemyUnitOfWork(session_factory)
    )
    app.dependency_overrides[get_audit_event_use_case] = lambda: GetAuditEventUseCase(
        SqlAlchemyUnitOfWork(session_factory)
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client, raw_api_key, str(user_id)


async def seed_complete_e2e_operator(
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
                email=UserEmail("complete.e2e.operator@example.test"),
                display_name=UserDisplayName("Complete E2E Operator"),
            )
        )
        role = await role_repository.create(
            Role.create(RoleName("complete-e2e-admin"), "Complete C1 integration operator.")
        )
        for permission_name, description in DEFAULT_PERMISSIONS:
            permission = await permission_repository.create(
                Permission.create(PermissionName(permission_name), description)
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
                name="complete e2e bootstrap key",
                granted_permissions=tuple(
                    permission_name for permission_name, _ in DEFAULT_PERMISSIONS
                ),
                scopes=("global",),
            )
        )
        await session.commit()
        return user.id


@pytest.mark.e2e
@pytest.mark.integration
@pytest.mark.anyio
async def test_complete_rest_api_to_postgres_product_workflow(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async for client, raw_api_key, owner_id in create_complete_e2e_client(session_factory):
        login = await client.post("/v1/auth/session", json={"api_key": raw_api_key})
        assert login.status_code == 201
        assert login.json()["user"]["email"] == "complete.e2e.operator@example.test"
        assert "mcp_sm_session=" in login.headers["set-cookie"]

        current_session = await client.get("/v1/auth/session")
        assert current_session.status_code == 200
        assert current_session.json()["user"]["id"] == owner_id

        created_vault = await client.post(
            "/v1/vaults",
            headers={"X-Request-ID": "req-c1-vault"},
            json={"name": "C1 Production", "description": "C1 controlled vault"},
        )
        assert created_vault.status_code == 201
        vault_id = created_vault.json()["id"]

        created_project = await client.post(
            f"/v1/vaults/{vault_id}/projects",
            headers={"X-Request-ID": "req-c1-project"},
            json={"name": "C1 API", "description": "C1 service project"},
        )
        assert created_project.status_code == 201
        project_id = created_project.json()["id"]

        created_secret = await client.post(
            f"/v1/projects/{project_id}/secrets",
            headers={"X-Request-ID": "req-c1-secret"},
            json={
                "key": "C1_DATABASE_PASSWORD",
                "description": "C1 non-sensitive metadata",
                "type": "password",
                "metadata": {"owner": "platform"},
                "tags": ["c1", "database"],
            },
        )
        assert created_secret.status_code == 201
        secret_id = created_secret.json()["id"]
        assert "value" not in created_secret.text

        initial_version = await client.post(
            f"/v1/secrets/{secret_id}/versions",
            json={"value": "not-a-real-secret-v1"},
        )
        assert initial_version.status_code == 201
        assert initial_version.json()["version"] == 1
        assert "not-a-real-secret-v1" not in initial_version.text

        rotated_version = await client.post(
            f"/v1/secrets/{secret_id}/versions",
            headers={"X-Request-ID": "req-c1-rotate"},
            json={"value": "not-a-real-secret-v2"},
        )
        assert rotated_version.status_code == 201
        assert rotated_version.json()["version"] == 2
        assert rotated_version.json()["active"] is True
        assert "not-a-real-secret-v2" not in rotated_version.text

        versions = await client.get(f"/v1/secrets/{secret_id}/versions")
        assert versions.status_code == 200
        assert [version["version"] for version in versions.json()] == [1, 2]
        assert [version["active"] for version in versions.json()] == [False, True]
        assert "not-a-real-secret" not in versions.text

        secret_value = await client.get(
            f"/v1/secrets/{secret_id}/versions/latest",
            headers={"X-Request-ID": "req-c1-secret-read"},
        )
        assert secret_value.status_code == 200
        assert secret_value.json()["value"] == "not-a-real-secret-v2"

        created_api_key = await client.post(
            "/v1/api-keys",
            headers={"X-Request-ID": "req-c1-api-key"},
            json={
                "name": "c1-api-consumer",
                "description": "C1 generated API key",
                "owner_id": owner_id,
                "owner_type": "user",
                "permissions": ["secret.read"],
                "scopes": ["global"],
            },
        )
        assert created_api_key.status_code == 201
        created_api_key_payload = created_api_key.json()
        api_key_id = created_api_key_payload["id"]
        assert created_api_key_payload["api_key"].startswith(created_api_key_payload["key_prefix"])

        listed_api_keys = await client.get("/v1/api-keys", params={"q": "c1-api-consumer"})
        assert listed_api_keys.status_code == 200
        assert [api_key["id"] for api_key in listed_api_keys.json()["data"]] == [api_key_id]
        assert "api_key" not in listed_api_keys.text

        revoked_api_key = await client.post(
            f"/v1/api-keys/{api_key_id}/revoke",
            headers={"X-Request-ID": "req-c1-api-key-revoke"},
        )
        assert revoked_api_key.status_code == 200
        assert revoked_api_key.json()["status"] == "revoked"

        permissions = await client.get("/v1/permissions")
        assert permissions.status_code == 200
        permission_ids_by_name = {
            permission["name"]: permission["id"] for permission in permissions.json()["data"]
        }
        role = await client.post(
            "/v1/roles",
            headers={"X-Request-ID": "req-c1-role"},
            json={
                "name": "c1-secret-reader",
                "description": "C1 custom role",
                "permission_ids": [permission_ids_by_name["secret.read"]],
            },
        )
        assert role.status_code == 201
        role_id = role.json()["id"]

        assigned_role = await client.post(
            f"/v1/actors/{owner_id}/roles/{role_id}",
            headers={"X-Request-ID": "req-c1-role-assign"},
        )
        assert assigned_role.status_code == 201
        assert assigned_role.json()["role_id"] == role_id

        role_assignments = await client.get(f"/v1/actors/{owner_id}/roles")
        assert role_assignments.status_code == 200
        assert role_id in {assignment["role_id"] for assignment in role_assignments.json()["data"]}

        revoked_role = await client.delete(
            f"/v1/actors/{owner_id}/roles/{role_id}",
            headers={"X-Request-ID": "req-c1-role-revoke"},
        )
        assert revoked_role.status_code == 200
        assert revoked_role.json()["status"] == "revoked"

        audit = await client.get("/v1/audit/events", params={"limit": 200})
        assert audit.status_code == 200
        events = audit.json()
        observed_actions = {event["action"] for event in events}
        assert {
            "session.create",
            "vault.create",
            "project.create",
            "secret.create",
            "secret.rotate",
            "secret.decrypt",
            "apikey.create",
            "apikey.revoke",
            "role.create",
            "role.assign",
            "role.revoke",
        }.issubset(observed_actions)
        assert "not-a-real-secret-v1" not in audit.text
        assert "not-a-real-secret-v2" not in audit.text

        vault_audit = await client.get(
            "/v1/audit/events",
            params={"action": "vault.create", "resource_id": vault_id, "limit": 10},
        )
        assert vault_audit.status_code == 200
        assert vault_audit.json()[0]["request_id"] == "req-c1-vault"

        logout = await client.delete("/v1/auth/session")
        assert logout.status_code == 204

        after_logout = await client.get("/v1/auth/session")
        assert after_logout.status_code == 401

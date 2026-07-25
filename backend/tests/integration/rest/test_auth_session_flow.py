from __future__ import annotations

import os
from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from application.audit.use_cases import PersistentAuditRecorder
from application.identity.use_cases import (
    AuthenticateApiKeyUseCase,
    AuthenticateSessionUseCase,
    CreateSessionUseCase,
    GetAccountSecurityUseCase,
    GetCurrentProfileUseCase,
    GetCurrentSessionUseCase,
    GetSettingsUseCase,
    ListActiveSessionsUseCase,
    RevokeCurrentSessionUseCase,
    RevokeSessionUseCase,
    UpdateCurrentProfileUseCase,
    UpdateNotificationsUseCase,
    UpdatePreferencesUseCase,
)
from domain.identity.entities import ApiKey, User
from domain.identity.value_objects import ApiKeyOwnerType, UserDisplayName, UserEmail
from infrastructure.identity import (
    Argon2idApiKeyHasher,
    SecureApiKeySecretGenerator,
    SecureSessionTokenGenerator,
)
from infrastructure.persistence import Base, SqlAlchemyApiKeyRepository, SqlAlchemyUnitOfWork
from infrastructure.persistence.identity_repositories import SqlAlchemyUserRepository
from presentation.rest.app import create_app
from presentation.rest.dependencies import (
    get_account_security_use_case,
    get_create_session_use_case,
    get_current_profile_use_case,
    get_current_session_use_case,
    get_list_active_sessions_use_case,
    get_revoke_current_session_use_case,
    get_revoke_session_use_case,
    get_settings_use_case,
    get_update_current_profile_use_case,
    get_update_notifications_use_case,
    get_update_preferences_use_case,
)

TEST_SCHEMA = "mcp_secret_manager_auth_session_flow_test"


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


async def create_authenticated_session_client(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[tuple[AsyncClient, str]]:
    generator = SecureApiKeySecretGenerator()
    hasher = Argon2idApiKeyHasher()
    session_token_generator = SecureSessionTokenGenerator()
    session_token_hasher = Argon2idApiKeyHasher()
    raw_api_key = generator.generate()
    key_prefix = generator.extract_prefix(raw_api_key)
    assert key_prefix is not None

    async with session_factory() as session:
        user = await SqlAlchemyUserRepository(session).create(
            User.create(
                email=UserEmail("session.operator@example.test"),
                display_name=UserDisplayName("Session Operator"),
            )
        )
        await SqlAlchemyApiKeyRepository(session).create(
            ApiKey.create(
                hashed_key=hasher.hash(raw_api_key),
                key_prefix=key_prefix,
                owner_id=user.id,
                owner_type=ApiKeyOwnerType.USER,
                expires_at=None,
            )
        )
        await session.commit()

    audit_recorder = PersistentAuditRecorder(SqlAlchemyUnitOfWork(session_factory))
    app = create_app(
        service_name="test-service",
        authenticate_api_key_use_case=AuthenticateApiKeyUseCase(
            SqlAlchemyUnitOfWork(session_factory),
            generator,
            hasher,
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
        generator,
        hasher,
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
    app.dependency_overrides[get_current_profile_use_case] = lambda: GetCurrentProfileUseCase(
        SqlAlchemyUnitOfWork(session_factory)
    )
    app.dependency_overrides[get_update_current_profile_use_case] = lambda: (
        UpdateCurrentProfileUseCase(
            SqlAlchemyUnitOfWork(session_factory),
            audit_recorder=audit_recorder,
        )
    )
    app.dependency_overrides[get_account_security_use_case] = lambda: GetAccountSecurityUseCase()
    app.dependency_overrides[get_list_active_sessions_use_case] = lambda: ListActiveSessionsUseCase(
        SqlAlchemyUnitOfWork(session_factory)
    )
    app.dependency_overrides[get_revoke_session_use_case] = lambda: RevokeSessionUseCase(
        SqlAlchemyUnitOfWork(session_factory),
        audit_recorder=audit_recorder,
    )
    app.dependency_overrides[get_settings_use_case] = lambda: GetSettingsUseCase(
        SqlAlchemyUnitOfWork(session_factory),
        service_name="test-service",
        environment="test",
    )
    app.dependency_overrides[get_update_preferences_use_case] = lambda: UpdatePreferencesUseCase(
        SqlAlchemyUnitOfWork(session_factory),
        audit_recorder=audit_recorder,
    )
    app.dependency_overrides[get_update_notifications_use_case] = lambda: (
        UpdateNotificationsUseCase(
            SqlAlchemyUnitOfWork(session_factory),
            audit_recorder=audit_recorder,
        )
    )

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client, raw_api_key


@pytest.mark.integration
@pytest.mark.anyio
async def test_api_key_session_browser_to_postgres_flow(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async for client, raw_api_key in create_authenticated_session_client(session_factory):
        created = await client.post("/v1/auth/session", json={"api_key": raw_api_key})

        assert created.status_code == 201
        assert "mcp_sm_session=" in created.headers["set-cookie"]

        response = await client.get("/v1/auth/session")
        assert response.status_code == 200
        assert response.json()["auth_method"] == "api_key"
        assert response.json()["user"]["email"] == "session.operator@example.test"
        assert response.json()["user"]["name"] == "Session Operator"

        profile = await client.patch(
            "/v1/me/profile",
            json={
                "email": "session.operator@example.test",
                "name": "Session Operator Updated",
                "organization": "Operations",
            },
        )
        assert profile.status_code == 200
        assert profile.json()["name"] == "Session Operator Updated"
        assert profile.json()["organization"] == "Operations"
        assert "api_key" not in profile.text

        preferences = await client.patch(
            "/v1/me/preferences",
            json={
                "date_time_format": "relative",
                "display_density": "compact",
                "language": "fr",
                "theme": "dark",
                "timezone": "Europe/Paris",
            },
        )
        assert preferences.status_code == 200
        assert preferences.json()["theme"] == "dark"

        settings = await client.get("/v1/me/settings")
        assert settings.status_code == 200
        assert settings.json()["preferences"]["timezone"] == "Europe/Paris"

        sessions = await client.get("/v1/me/sessions")
        assert sessions.status_code == 200
        assert sessions.json()["data"][0]["current"] is True
        assert "mcp_sm_session_" not in sessions.text

        revoked = await client.delete("/v1/auth/session")
        assert revoked.status_code == 204

        after_revoke = await client.get("/v1/auth/session")
        assert after_revoke.status_code == 401

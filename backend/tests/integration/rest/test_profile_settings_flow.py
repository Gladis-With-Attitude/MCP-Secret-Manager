from __future__ import annotations

import os
from collections.abc import AsyncIterator, Callable
from datetime import UTC, datetime, timedelta

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from application.audit.use_cases import PersistentAuditRecorder
from application.identity.use_cases import (
    AuthenticateApiKeyUseCase,
    ChangePasswordUseCase,
    GetAccountSecurityUseCase,
    GetCurrentProfileUseCase,
    GetSettingsUseCase,
    ListActiveSessionsUseCase,
    RevokeSessionUseCase,
    UpdateCurrentProfileUseCase,
    UpdateNotificationsUseCase,
    UpdatePreferencesUseCase,
)
from domain.identity.entities import ApiKey, AuthSession, User
from domain.identity.value_objects import ApiKeyOwnerType, UserDisplayName, UserEmail
from infrastructure.identity import Argon2idApiKeyHasher, SecureApiKeySecretGenerator
from infrastructure.persistence import (
    Base,
    SqlAlchemyApiKeyRepository,
    SqlAlchemyAuthSessionRepository,
    SqlAlchemyUnitOfWork,
    SqlAlchemyUserRepository,
)
from presentation.rest.app import create_app
from presentation.rest.dependencies import (
    get_account_security_use_case,
    get_change_password_use_case,
    get_current_profile_use_case,
    get_list_active_sessions_use_case,
    get_revoke_session_use_case,
    get_settings_use_case,
    get_update_current_profile_use_case,
    get_update_notifications_use_case,
    get_update_preferences_use_case,
)

TEST_SCHEMA = "mcp_secret_manager_profile_settings_flow_test"


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


async def create_authenticated_profile_client(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncClient]:
    generator = SecureApiKeySecretGenerator()
    hasher = Argon2idApiKeyHasher()
    raw_api_key = generator.generate()
    key_prefix = generator.extract_prefix(raw_api_key)
    assert key_prefix is not None
    await seed_profile_operator(session_factory, raw_api_key, key_prefix, hasher)

    audit_recorder = PersistentAuditRecorder(SqlAlchemyUnitOfWork(session_factory))
    app = create_app(
        service_name="profile-settings-test",
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

    app.dependency_overrides[get_current_profile_use_case] = use_case_factory(
        GetCurrentProfileUseCase
    )
    app.dependency_overrides[get_update_current_profile_use_case] = lambda: (
        UpdateCurrentProfileUseCase(
            SqlAlchemyUnitOfWork(session_factory),
            audit_recorder=audit_recorder,
        )
    )
    app.dependency_overrides[get_account_security_use_case] = lambda: GetAccountSecurityUseCase()
    app.dependency_overrides[get_list_active_sessions_use_case] = use_case_factory(
        ListActiveSessionsUseCase
    )
    app.dependency_overrides[get_revoke_session_use_case] = lambda: RevokeSessionUseCase(
        SqlAlchemyUnitOfWork(session_factory),
        audit_recorder=audit_recorder,
    )
    app.dependency_overrides[get_change_password_use_case] = lambda: ChangePasswordUseCase()
    app.dependency_overrides[get_settings_use_case] = lambda: GetSettingsUseCase(
        SqlAlchemyUnitOfWork(session_factory),
        service_name="profile-settings-test",
        environment="test",
        backend_version="0.1.0",
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
    async with AsyncClient(
        transport=transport,
        base_url="http://testserver",
        headers={"Authorization": f"Bearer {raw_api_key}"},
    ) as client:
        yield client


async def seed_profile_operator(
    session_factory: async_sessionmaker[AsyncSession],
    raw_api_key: str,
    key_prefix: str,
    hasher: Argon2idApiKeyHasher,
) -> None:
    async with session_factory() as session:
        user_repository = SqlAlchemyUserRepository(session)
        api_key_repository = SqlAlchemyApiKeyRepository(session)
        auth_session_repository = SqlAlchemyAuthSessionRepository(session)

        user = await user_repository.create(
            User.create(
                email=UserEmail("profile.operator@example.test"),
                display_name=UserDisplayName("Profile Operator"),
            )
        )
        api_key = await api_key_repository.create(
            ApiKey.create(
                hashed_key=hasher.hash(raw_api_key),
                key_prefix=key_prefix,
                owner_id=user.id,
                owner_type=ApiKeyOwnerType.USER,
                expires_at=None,
                name="bootstrap profile key",
                granted_permissions=("profile.read",),
                scopes=("global",),
            )
        )
        await auth_session_repository.create(
            AuthSession.create(
                hashed_token="hashed-session-token",  # noqa: S106
                token_prefix="mcp_sm_session_0123456789abcdef",  # noqa: S106
                api_key_id=api_key.id,
                owner_id=user.id,
                owner_type=ApiKeyOwnerType.USER,
                expires_at=datetime.now(UTC) + timedelta(hours=1),
            ).mark_seen()
        )
        await session.commit()


@pytest.mark.integration
@pytest.mark.anyio
async def test_profile_settings_browser_to_postgres_flow(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async for client in create_authenticated_profile_client(session_factory):
        profile = await client.get("/v1/me/profile")
        assert profile.status_code == 200
        assert profile.json()["email"] == "profile.operator@example.test"
        assert profile.json()["name"] == "Profile Operator"
        assert profile.json()["organization"] is None

        updated_profile = await client.patch(
            "/v1/me/profile",
            json={
                "email": "profile.operator@example.test",
                "name": "Updated Operator",
                "organization": "Secret Ops",
            },
        )
        assert updated_profile.status_code == 200
        assert updated_profile.json()["name"] == "Updated Operator"
        assert updated_profile.json()["organization"] == "Secret Ops"

        rejected_email_change = await client.patch(
            "/v1/me/profile",
            json={
                "email": "renamed@example.test",
                "name": "Updated Operator",
                "organization": "Secret Ops",
            },
        )
        assert rejected_email_change.status_code == 400

        security = await client.get("/v1/me/security")
        assert security.status_code == 200
        assert security.json()["password_change_available"] is False

        settings = await client.get("/v1/me/settings")
        assert settings.status_code == 200
        assert settings.json()["public_settings"]["instance_name"] == "profile-settings-test"
        assert settings.json()["preferences"]["theme"] == "system"
        assert settings.json()["notifications"]["security_alerts"] is True

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
        assert preferences.json()["date_time_format"] == "relative"
        assert preferences.json()["display_density"] == "compact"

        notifications = await client.patch(
            "/v1/me/notifications",
            json={
                "audit_alerts": False,
                "email_enabled": False,
                "in_app_enabled": True,
                "product_updates": True,
                "security_alerts": True,
            },
        )
        assert notifications.status_code == 200
        assert notifications.json()["audit_alerts"] is False
        assert notifications.json()["product_updates"] is True

        persisted_settings = await client.get("/v1/me/settings")
        assert persisted_settings.status_code == 200
        assert persisted_settings.json()["preferences"]["timezone"] == "Europe/Paris"
        assert persisted_settings.json()["notifications"]["email_enabled"] is False

        sessions = await client.get("/v1/me/sessions")
        assert sessions.status_code == 200
        session_payload = sessions.json()["data"]
        assert len(session_payload) == 1
        session_id = session_payload[0]["id"]
        assert session_payload[0]["current"] is False
        assert "token" not in session_payload[0]
        assert "hashed_token" not in session_payload[0]

        revoked = await client.delete(f"/v1/me/sessions/{session_id}")
        assert revoked.status_code == 204

        remaining_sessions = await client.get("/v1/me/sessions")
        assert remaining_sessions.status_code == 200
        assert remaining_sessions.json()["data"] == []

        password = await client.post(
            "/v1/me/password",
            json={"current_password": "old secret", "new_password": "new secret"},
        )
        assert password.status_code == 400

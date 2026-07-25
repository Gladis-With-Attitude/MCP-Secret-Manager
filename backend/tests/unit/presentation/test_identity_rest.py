from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated, cast

import anyio
from fastapi import Depends, FastAPI
from httpx import ASGITransport, AsyncClient

from application.audit.dto import AuditContext
from application.identity.dto import (
    AccountSecurityResponse,
    ActiveSessionListResponse,
    ActiveSessionResponse,
    ApiKeyCreatedResponse,
    ApiKeyListResponse,
    ApiKeyPaginationResponse,
    ApiKeyPermissionsResponse,
    ApiKeyResponse,
    AuthenticatedIdentityResponse,
    ChangePasswordRequest,
    CreateApiKeyRequest,
    CreateServiceAccountRequest,
    CreateSessionRequest,
    CreateUserRequest,
    CurrentSessionResponse,
    GetApiKeyRequest,
    GetProfileRequest,
    GetSettingsRequest,
    ListActiveSessionsRequest,
    ListApiKeysRequest,
    NotificationPreferencesResponse,
    ProfilePermissionsResponse,
    PublicSettingsResponse,
    RevokeApiKeyRequest,
    RevokeSessionRequest,
    ServiceAccountResponse,
    SessionCreatedResponse,
    SettingsPermissionsResponse,
    SettingsResponse,
    UpdateApiKeyRequest,
    UpdateNotificationsRequest,
    UpdatePreferencesRequest,
    UpdateProfileRequest,
    UserPreferencesResponse,
    UserProfileResponse,
    UserResponse,
)
from application.identity.exceptions import AuthenticationFailedError
from application.identity.use_cases import AuthenticateApiKeyUseCase, AuthenticateSessionUseCase
from application.rbac.dto import AuthorizationDecision, RequirePermission
from presentation.rest.app import create_app
from presentation.rest.authentication import (
    CSRF_COOKIE_NAME,
    CSRF_HEADER_NAME,
    SESSION_COOKIE_NAME,
    AuthenticatedIdentity,
    get_authenticated_identity,
)
from presentation.rest.dependencies import (
    get_account_security_use_case,
    get_api_key_use_case,
    get_authorize_use_case,
    get_change_password_use_case,
    get_create_api_key_use_case,
    get_create_service_account_use_case,
    get_create_session_use_case,
    get_create_user_use_case,
    get_current_profile_use_case,
    get_current_session_use_case,
    get_list_active_sessions_use_case,
    get_list_api_keys_use_case,
    get_revoke_api_key_use_case,
    get_revoke_session_use_case,
    get_settings_use_case,
    get_update_api_key_use_case,
    get_update_current_profile_use_case,
    get_update_notifications_use_case,
    get_update_preferences_use_case,
)


class FakeCreateUserUseCase:
    async def execute(self, request: CreateUserRequest) -> UserResponse:
        return UserResponse(
            id="a6ef559c-b860-4028-a050-bb7bd2244916",
            email=request.email.strip().lower(),
            display_name=request.display_name.strip(),
            status="active",
            created_at="2026-07-21T12:00:00+00:00",
        )


class FakeCreateServiceAccountUseCase:
    async def execute(self, request: CreateServiceAccountRequest) -> ServiceAccountResponse:
        return ServiceAccountResponse(
            id="8891741f-bdc3-49c4-b2e1-c64c37d1ba50",
            project_id=request.project_id,
            name=request.name,
            description=request.description,
            status="active",
            created_at="2026-07-21T12:00:00+00:00",
        )


class FakeCreateApiKeyUseCase:
    async def execute(self, request: CreateApiKeyRequest) -> ApiKeyCreatedResponse:
        return ApiKeyCreatedResponse(
            id="71a35966-aa7e-48af-815a-77796de636af",
            api_key="mcp_sm_0123456789abcdef_0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef",
            name=request.name or "agent",
            description=request.description,
            key_prefix="mcp_sm_0123456789abcdef",
            owner_id=request.owner_id,
            owner_type=request.owner_type,
            granted_permissions=request.granted_permissions,
            scopes=request.scopes,
            status="active",
            expires_at=request.expires_at,
            revoked_at=None,
            created_at="2026-07-21T12:00:00+00:00",
        )


class FakeListApiKeysUseCase:
    async def execute(self, request: ListApiKeysRequest) -> ApiKeyListResponse:
        return ApiKeyListResponse(
            data=(
                ApiKeyResponse(
                    id="71a35966-aa7e-48af-815a-77796de636af",
                    name="agent",
                    description="Production agent",
                    key_prefix="mcp_sm_0123456789abcdef",
                    owner_id="a6ef559c-b860-4028-a050-bb7bd2244916",
                    owner_type="user",
                    granted_permissions=("secret.read",),
                    scopes=("global",),
                    status=request.status or "active",
                    expires_at=None,
                    revoked_at=None,
                    created_at="2026-07-21T12:00:00+00:00",
                ),
            ),
            pagination=ApiKeyPaginationResponse(
                page=request.page,
                page_size=request.page_size,
                total=1,
                has_next_page=False,
                has_previous_page=False,
            ),
            permissions=ApiKeyPermissionsResponse(create=True, read=True, revoke=True, update=True),
        )


class FakeGetApiKeyUseCase:
    async def execute(self, request: GetApiKeyRequest) -> ApiKeyResponse:
        return ApiKeyResponse(
            id=request.api_key_id,
            name="agent",
            description="Production agent",
            key_prefix="mcp_sm_0123456789abcdef",
            owner_id="a6ef559c-b860-4028-a050-bb7bd2244916",
            owner_type="user",
            granted_permissions=("secret.read",),
            scopes=("global",),
            status="active",
            expires_at=None,
            revoked_at=None,
            created_at="2026-07-21T12:00:00+00:00",
        )


class FakeRevokeApiKeyUseCase:
    async def execute(self, request: RevokeApiKeyRequest) -> ApiKeyResponse:
        return ApiKeyResponse(
            id=request.api_key_id,
            name="agent",
            description="Production agent",
            key_prefix="mcp_sm_0123456789abcdef",
            owner_id="a6ef559c-b860-4028-a050-bb7bd2244916",
            owner_type="user",
            granted_permissions=("secret.read",),
            scopes=("global",),
            status="revoked",
            expires_at=None,
            revoked_at="2026-07-21T12:30:00+00:00",
            created_at="2026-07-21T12:00:00+00:00",
        )


class FakeUpdateApiKeyUseCase:
    async def execute(self, request: UpdateApiKeyRequest) -> ApiKeyResponse:
        return ApiKeyResponse(
            id=request.api_key_id,
            name=request.name or "agent",
            description=request.description,
            key_prefix="mcp_sm_0123456789abcdef",
            owner_id="a6ef559c-b860-4028-a050-bb7bd2244916",
            owner_type="user",
            granted_permissions=request.granted_permissions,
            scopes=request.scopes,
            status="active",
            expires_at=request.expires_at,
            revoked_at=None,
            created_at="2026-07-21T12:00:00+00:00",
        )


class FakeAuthorizeUseCase:
    async def execute(self, _request: RequirePermission) -> AuthorizationDecision:
        return AuthorizationDecision(allowed=True)


class FakeAuthenticateApiKeyUseCase:
    async def execute(
        self,
        raw_api_key: str,
        audit_context: AuditContext | None = None,
    ) -> AuthenticatedIdentityResponse:
        assert audit_context is not None
        if raw_api_key != "valid-api-key":
            raise AuthenticationFailedError("Invalid API key.")
        return AuthenticatedIdentityResponse(
            id="a6ef559c-b860-4028-a050-bb7bd2244916",
            type="user",
            api_key_id="71a35966-aa7e-48af-815a-77796de636af",
        )


class FakeAuthenticateSessionUseCase:
    async def execute(self, session_token: str) -> AuthenticatedIdentityResponse:
        if session_token != FAKE_BROWSER_SESSION_VALUE:
            raise AuthenticationFailedError("Invalid session.")
        return AuthenticatedIdentityResponse(
            id="a6ef559c-b860-4028-a050-bb7bd2244916",
            type="user",
            api_key_id="71a35966-aa7e-48af-815a-77796de636af",
            session_id="c890ab63-7337-4da3-a380-987f69aa3bdb",
        )


class FakeGetCurrentSessionUseCase:
    async def execute(
        self, api_key_id: str, session_id: str | None = None
    ) -> CurrentSessionResponse:
        _ = session_id
        return CurrentSessionResponse(
            api_key_id=api_key_id,
            auth_method="api_key",
            expires_at=None,
            issued_at="2026-07-21T12:00:00+00:00",
            user_id="a6ef559c-b860-4028-a050-bb7bd2244916",
            user_type="user",
            email="user@example.test",
            name="Ada Lovelace",
            profile_label="User",
        )


FAKE_BROWSER_SESSION_VALUE = (
    "mcp_sm_session_0123456789abcdef_"
    "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
)


class FakeCreateSessionUseCase:
    async def execute(self, request: CreateSessionRequest) -> SessionCreatedResponse:
        if request.api_key != "valid-api-key":
            raise AuthenticationFailedError("Invalid API key.")
        return SessionCreatedResponse(
            session_token=FAKE_BROWSER_SESSION_VALUE,
            session=CurrentSessionResponse(
                api_key_id="71a35966-aa7e-48af-815a-77796de636af",
                auth_method="api_key",
                expires_at=None,
                issued_at="2026-07-21T12:00:00+00:00",
                user_id="a6ef559c-b860-4028-a050-bb7bd2244916",
                user_type="user",
                email="user@example.test",
                name="Ada Lovelace",
                profile_label="User",
            ),
        )


class FakeGetCurrentProfileUseCase:
    async def execute(self, request: GetProfileRequest) -> UserProfileResponse:
        return UserProfileResponse(
            id=request.identity_id,
            email="user@example.test",
            name="Ada Lovelace",
            account_type="human",
            avatar_url=None,
            organization="Analytical Engines",
            email_editable=False,
            primary_role=None,
            last_login_at=None,
            created_at="2026-07-21T12:00:00+00:00",
            permissions=ProfilePermissionsResponse(
                change_password=False,
                read=True,
                revoke_sessions=True,
                update=True,
            ),
        )


class FakeUpdateCurrentProfileUseCase:
    async def execute(self, request: UpdateProfileRequest) -> UserProfileResponse:
        return UserProfileResponse(
            id=request.identity_id,
            email=request.email or "user@example.test",
            name=request.name,
            account_type="human",
            avatar_url=None,
            organization=request.organization,
            email_editable=False,
            primary_role=None,
            last_login_at=None,
            created_at="2026-07-21T12:00:00+00:00",
            permissions=ProfilePermissionsResponse(
                change_password=False,
                read=True,
                revoke_sessions=True,
                update=True,
            ),
        )


class FakeGetAccountSecurityUseCase:
    async def execute(self) -> AccountSecurityResponse:
        return AccountSecurityResponse(
            mfa_enabled=False,
            passkeys_enabled=False,
            password_change_available=False,
            recovery_keys_available=False,
            webauthn_enabled=False,
        )


class FakeListActiveSessionsUseCase:
    async def execute(self, request: ListActiveSessionsRequest) -> ActiveSessionListResponse:
        return ActiveSessionListResponse(
            data=(
                ActiveSessionResponse(
                    id=request.current_session_id or "c890ab63-7337-4da3-a380-987f69aa3bdb",
                    current=True,
                    device=None,
                    expires_at="2026-07-22T00:00:00+00:00",
                    ip_address=None,
                    last_seen_at="2026-07-21T12:00:00+00:00",
                    location=None,
                    user_agent=None,
                ),
            ),
            permissions=ProfilePermissionsResponse(
                change_password=False,
                read=True,
                revoke_sessions=True,
                update=True,
            ),
        )


class FakeRevokeSessionUseCase:
    async def execute(self, request: RevokeSessionRequest) -> None:
        assert request.session_id


class FakeChangePasswordUseCase:
    async def execute(self, request: ChangePasswordRequest) -> None:
        assert request.current_password
        assert request.new_password


class FakeGetSettingsUseCase:
    async def execute(self, _request: GetSettingsRequest) -> SettingsResponse:
        return SettingsResponse(
            notifications=NotificationPreferencesResponse(
                audit_alerts=True,
                email_enabled=True,
                in_app_enabled=True,
                product_updates=False,
                security_alerts=True,
            ),
            permissions=SettingsPermissionsResponse(
                read=True,
                update=True,
                update_notifications=True,
                update_preferences=True,
            ),
            preferences=UserPreferencesResponse(
                date_time_format="absolute",
                display_density="comfortable",
                language="en",
                theme="system",
                timezone="UTC",
            ),
            public_settings=PublicSettingsResponse(
                api_status="healthy",
                backend_version="0.1.0",
                deployment_mode=None,
                environment="test",
                frontend_version=None,
                instance_name="test-service",
                public_url=None,
            ),
        )


class FakeUpdatePreferencesUseCase:
    async def execute(self, request: UpdatePreferencesRequest) -> UserPreferencesResponse:
        return UserPreferencesResponse(
            date_time_format=request.date_time_format,
            display_density=request.display_density,
            language=request.language,
            theme=request.theme,
            timezone=request.timezone,
        )


class FakeUpdateNotificationsUseCase:
    async def execute(
        self,
        request: UpdateNotificationsRequest,
    ) -> NotificationPreferencesResponse:
        return NotificationPreferencesResponse(
            audit_alerts=request.audit_alerts,
            email_enabled=request.email_enabled,
            in_app_enabled=request.in_app_enabled,
            product_updates=request.product_updates,
            security_alerts=request.security_alerts,
        )


async def build_identity_app() -> FastAPI:
    app = create_app(
        service_name="test-service",
        authenticate_api_key_use_case=cast(
            AuthenticateApiKeyUseCase,
            FakeAuthenticateApiKeyUseCase(),
        ),
        authenticate_session_use_case=cast(
            AuthenticateSessionUseCase,
            FakeAuthenticateSessionUseCase(),
        ),
    )

    async def create_user_dependency() -> AsyncIterator[FakeCreateUserUseCase]:
        yield FakeCreateUserUseCase()

    async def create_service_account_dependency() -> AsyncIterator[FakeCreateServiceAccountUseCase]:
        yield FakeCreateServiceAccountUseCase()

    async def create_api_key_dependency() -> AsyncIterator[FakeCreateApiKeyUseCase]:
        yield FakeCreateApiKeyUseCase()

    async def create_session_dependency() -> AsyncIterator[FakeCreateSessionUseCase]:
        yield FakeCreateSessionUseCase()

    async def current_session_dependency() -> AsyncIterator[FakeGetCurrentSessionUseCase]:
        yield FakeGetCurrentSessionUseCase()

    async def current_profile_dependency() -> AsyncIterator[FakeGetCurrentProfileUseCase]:
        yield FakeGetCurrentProfileUseCase()

    async def update_current_profile_dependency() -> AsyncIterator[FakeUpdateCurrentProfileUseCase]:
        yield FakeUpdateCurrentProfileUseCase()

    async def account_security_dependency() -> AsyncIterator[FakeGetAccountSecurityUseCase]:
        yield FakeGetAccountSecurityUseCase()

    async def list_active_sessions_dependency() -> AsyncIterator[FakeListActiveSessionsUseCase]:
        yield FakeListActiveSessionsUseCase()

    async def revoke_session_dependency() -> AsyncIterator[FakeRevokeSessionUseCase]:
        yield FakeRevokeSessionUseCase()

    async def change_password_dependency() -> AsyncIterator[FakeChangePasswordUseCase]:
        yield FakeChangePasswordUseCase()

    async def settings_dependency() -> AsyncIterator[FakeGetSettingsUseCase]:
        yield FakeGetSettingsUseCase()

    async def update_preferences_dependency() -> AsyncIterator[FakeUpdatePreferencesUseCase]:
        yield FakeUpdatePreferencesUseCase()

    async def update_notifications_dependency() -> AsyncIterator[FakeUpdateNotificationsUseCase]:
        yield FakeUpdateNotificationsUseCase()

    async def list_api_keys_dependency() -> AsyncIterator[FakeListApiKeysUseCase]:
        yield FakeListApiKeysUseCase()

    async def get_api_key_dependency() -> AsyncIterator[FakeGetApiKeyUseCase]:
        yield FakeGetApiKeyUseCase()

    async def revoke_api_key_dependency() -> AsyncIterator[FakeRevokeApiKeyUseCase]:
        yield FakeRevokeApiKeyUseCase()

    async def update_api_key_dependency() -> AsyncIterator[FakeUpdateApiKeyUseCase]:
        yield FakeUpdateApiKeyUseCase()

    async def authorize_dependency() -> AsyncIterator[FakeAuthorizeUseCase]:
        yield FakeAuthorizeUseCase()

    app.dependency_overrides[get_create_user_use_case] = create_user_dependency
    app.dependency_overrides[get_create_service_account_use_case] = (
        create_service_account_dependency
    )
    app.dependency_overrides[get_create_api_key_use_case] = create_api_key_dependency
    app.dependency_overrides[get_list_api_keys_use_case] = list_api_keys_dependency
    app.dependency_overrides[get_api_key_use_case] = get_api_key_dependency
    app.dependency_overrides[get_update_api_key_use_case] = update_api_key_dependency
    app.dependency_overrides[get_revoke_api_key_use_case] = revoke_api_key_dependency
    app.dependency_overrides[get_create_session_use_case] = create_session_dependency
    app.dependency_overrides[get_current_session_use_case] = current_session_dependency
    app.dependency_overrides[get_current_profile_use_case] = current_profile_dependency
    app.dependency_overrides[get_update_current_profile_use_case] = (
        update_current_profile_dependency
    )
    app.dependency_overrides[get_account_security_use_case] = account_security_dependency
    app.dependency_overrides[get_list_active_sessions_use_case] = list_active_sessions_dependency
    app.dependency_overrides[get_revoke_session_use_case] = revoke_session_dependency
    app.dependency_overrides[get_change_password_use_case] = change_password_dependency
    app.dependency_overrides[get_settings_use_case] = settings_dependency
    app.dependency_overrides[get_update_preferences_use_case] = update_preferences_dependency
    app.dependency_overrides[get_update_notifications_use_case] = update_notifications_dependency
    app.dependency_overrides[get_authorize_use_case] = authorize_dependency
    return app


def test_create_user_endpoint_returns_created_user() -> None:
    async def run() -> None:
        app = await build_identity_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.post(
                "/v1/users",
                json={"email": "USER@example.com", "display_name": " Ada Lovelace "},
            )

        assert response.status_code == 201
        assert response.json()["email"] == "user@example.com"
        assert response.json()["display_name"] == "Ada Lovelace"

    anyio.run(run)


def test_create_service_account_endpoint_returns_created_service_account() -> None:
    async def run() -> None:
        app = await build_identity_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.post(
                "/v1/service-accounts",
                json={
                    "project_id": "4b72f603-08db-4a6c-bd17-0bfe41dd773f",
                    "name": "openclaw-api",
                    "description": "OpenClaw API service account.",
                },
            )

        assert response.status_code == 201
        assert response.json()["name"] == "openclaw-api"
        assert response.json()["status"] == "active"

    anyio.run(run)


def test_create_api_key_endpoint_returns_full_key_once() -> None:
    async def run() -> None:
        app = await build_identity_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.post(
                "/v1/api-keys",
                headers={"Authorization": "Bearer valid-api-key"},
                json={
                    "name": "agent",
                    "description": "Production agent",
                    "owner_id": "a6ef559c-b860-4028-a050-bb7bd2244916",
                    "owner_type": "user",
                    "permissions": ["secret.read"],
                    "scopes": ["global"],
                },
            )

        payload = response.json()
        assert response.status_code == 201
        assert payload["api_key"].startswith("mcp_sm_0123456789abcdef_")
        assert payload["token"] == payload["api_key"]
        assert payload["name"] == "agent"
        assert payload["key_prefix"] == "mcp_sm_0123456789abcdef"
        assert payload["granted_permissions"] == ["secret.read"]
        assert "hashed_key" not in payload

    anyio.run(run)


def test_list_api_keys_endpoint_returns_metadata_only() -> None:
    async def run() -> None:
        app = await build_identity_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get(
                "/v1/api-keys",
                headers={"Authorization": "Bearer valid-api-key"},
                params={"page": 1, "page_size": 20, "status": "active"},
            )

        payload = response.json()
        assert response.status_code == 200
        assert payload["data"][0]["name"] == "agent"
        assert payload["data"][0]["key_prefix"] == "mcp_sm_0123456789abcdef"
        assert payload["permissions"] == {
            "create": True,
            "read": True,
            "revoke": True,
            "update": True,
        }
        assert "api_key" not in payload["data"][0]
        assert "hashed_key" not in payload["data"][0]

    anyio.run(run)


def test_get_api_key_endpoint_returns_metadata_only() -> None:
    async def run() -> None:
        app = await build_identity_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get(
                "/v1/api-keys/71a35966-aa7e-48af-815a-77796de636af",
                headers={"Authorization": "Bearer valid-api-key"},
            )

        payload = response.json()
        assert response.status_code == 200
        assert payload["id"] == "71a35966-aa7e-48af-815a-77796de636af"
        assert payload["name"] == "agent"
        assert "api_key" not in payload
        assert "hashed_key" not in payload

    anyio.run(run)


def test_update_api_key_endpoint_returns_metadata_only() -> None:
    async def run() -> None:
        app = await build_identity_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.patch(
                "/v1/api-keys/71a35966-aa7e-48af-815a-77796de636af",
                headers={"Authorization": "Bearer valid-api-key"},
                json={
                    "name": "updated agent",
                    "description": "Updated metadata",
                    "permissions": ["secret.read", "secret.rotate"],
                    "scopes": ["global"],
                },
            )

        payload = response.json()
        assert response.status_code == 200
        assert payload["id"] == "71a35966-aa7e-48af-815a-77796de636af"
        assert payload["name"] == "updated agent"
        assert payload["granted_permissions"] == ["secret.read", "secret.rotate"]
        assert payload["scopes"] == ["global"]
        assert "api_key" not in payload
        assert "token" not in payload
        assert "hashed_key" not in payload

    anyio.run(run)


def test_revoke_api_key_endpoint_returns_revoked_metadata() -> None:
    async def run() -> None:
        app = await build_identity_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.post(
                "/v1/api-keys/71a35966-aa7e-48af-815a-77796de636af/revoke",
                headers={"Authorization": "Bearer valid-api-key"},
            )

        payload = response.json()
        assert response.status_code == 200
        assert payload["status"] == "revoked"
        assert payload["revoked_at"] == "2026-07-21T12:30:00+00:00"
        assert "api_key" not in payload

    anyio.run(run)


def test_current_session_endpoint_returns_authenticated_session() -> None:
    async def run() -> None:
        app = await build_identity_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get(
                "/v1/auth/session",
                headers={"Authorization": "Bearer valid-api-key"},
            )

        payload = response.json()
        assert response.status_code == 200
        assert payload["auth_method"] == "api_key"
        assert payload["api_key_id"] == "71a35966-aa7e-48af-815a-77796de636af"
        assert payload["user"] == {
            "id": "a6ef559c-b860-4028-a050-bb7bd2244916",
            "type": "user",
            "email": "user@example.test",
            "name": "Ada Lovelace",
            "profile_label": "User",
        }

    anyio.run(run)


def test_profile_and_settings_endpoints_return_authenticated_user_data() -> None:
    async def run() -> None:
        app = await build_identity_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            profile = await client.get(
                "/v1/me/profile",
                headers={"Authorization": "Bearer valid-api-key"},
            )
            settings = await client.get(
                "/v1/me/settings",
                headers={"Authorization": "Bearer valid-api-key"},
            )
            security = await client.get(
                "/v1/me/security",
                headers={"Authorization": "Bearer valid-api-key"},
            )
            sessions = await client.get(
                "/v1/me/sessions",
                headers={"Authorization": "Bearer valid-api-key"},
            )

        assert profile.status_code == 200
        assert profile.json()["email"] == "user@example.test"
        assert profile.json()["permissions"]["update"] is True
        assert settings.status_code == 200
        assert settings.json()["preferences"]["theme"] == "system"
        assert settings.json()["notifications"]["security_alerts"] is True
        assert security.status_code == 200
        assert security.json()["password_change_available"] is False
        assert sessions.status_code == 200
        assert sessions.json()["data"][0]["current"] is True
        assert "token" not in sessions.text

    anyio.run(run)


def test_profile_and_settings_update_endpoints_return_safe_contracts() -> None:
    async def run() -> None:
        app = await build_identity_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            profile = await client.patch(
                "/v1/me/profile",
                headers={"Authorization": "Bearer valid-api-key"},
                json={
                    "email": "user@example.test",
                    "name": "Ada Byron",
                    "organization": "Analytical Engines",
                },
            )
            preferences = await client.patch(
                "/v1/me/preferences",
                headers={"Authorization": "Bearer valid-api-key"},
                json={
                    "date_time_format": "relative",
                    "display_density": "compact",
                    "language": "fr",
                    "theme": "dark",
                    "timezone": "Europe/Paris",
                },
            )
            notifications = await client.patch(
                "/v1/me/notifications",
                headers={"Authorization": "Bearer valid-api-key"},
                json={
                    "audit_alerts": False,
                    "email_enabled": False,
                    "in_app_enabled": True,
                    "product_updates": True,
                    "security_alerts": True,
                },
            )
            revoked = await client.delete(
                "/v1/me/sessions/c890ab63-7337-4da3-a380-987f69aa3bdb",
                headers={"Authorization": "Bearer valid-api-key"},
            )

        assert profile.status_code == 200
        assert profile.json()["name"] == "Ada Byron"
        assert preferences.status_code == 200
        assert preferences.json()["theme"] == "dark"
        assert preferences.json()["timezone"] == "Europe/Paris"
        assert notifications.status_code == 200
        assert notifications.json()["audit_alerts"] is False
        assert revoked.status_code == 204

    anyio.run(run)


def test_current_session_endpoint_requires_valid_authentication() -> None:
    async def run() -> None:
        app = await build_identity_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            missing = await client.get("/v1/auth/session")
            invalid = await client.get(
                "/v1/auth/session",
                headers={"Authorization": "Bearer invalid-api-key"},
            )

        assert missing.status_code == 401
        assert invalid.status_code == 401

    anyio.run(run)


def test_current_profile_endpoint_returns_authenticated_profile() -> None:
    async def run() -> None:
        app = await build_identity_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get(
                "/v1/me/profile",
                headers={"Authorization": "Bearer valid-api-key"},
            )

        payload = response.json()
        assert response.status_code == 200
        assert payload["id"] == "a6ef559c-b860-4028-a050-bb7bd2244916"
        assert payload["email"] == "user@example.test"
        assert payload["name"] == "Ada Lovelace"
        assert payload["organization"] == "Analytical Engines"
        assert payload["permissions"] == {
            "change_password": False,
            "read": True,
            "revoke_sessions": True,
            "update": True,
        }

    anyio.run(run)


def test_update_profile_endpoint_returns_updated_profile() -> None:
    async def run() -> None:
        app = await build_identity_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.patch(
                "/v1/me/profile",
                headers={"Authorization": "Bearer valid-api-key"},
                json={
                    "email": "ignored@example.test",
                    "name": "Grace Hopper",
                    "organization": "Compiler Lab",
                },
            )

        payload = response.json()
        assert response.status_code == 200
        assert payload["email"] == "ignored@example.test"
        assert payload["name"] == "Grace Hopper"
        assert payload["organization"] == "Compiler Lab"

    anyio.run(run)


def test_profile_security_endpoint_reports_password_unavailable() -> None:
    async def run() -> None:
        app = await build_identity_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get(
                "/v1/me/security",
                headers={"Authorization": "Bearer valid-api-key"},
            )

        assert response.status_code == 200
        assert response.json()["password_change_available"] is False

    anyio.run(run)


def test_active_sessions_endpoint_returns_metadata_only_sessions() -> None:
    async def run() -> None:
        app = await build_identity_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get(
                "/v1/me/sessions",
                headers={"Authorization": "Bearer valid-api-key"},
            )

        payload = response.json()
        assert response.status_code == 200
        assert payload["data"][0]["current"] is True
        assert payload["data"][0]["last_seen_at"] == "2026-07-21T12:00:00+00:00"
        assert payload["permissions"]["revoke_sessions"] is True
        assert "token" not in payload["data"][0]
        assert "hashed_token" not in payload["data"][0]

    anyio.run(run)


def test_revoke_session_endpoint_returns_no_content() -> None:
    async def run() -> None:
        app = await build_identity_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.delete(
                "/v1/me/sessions/c890ab63-7337-4da3-a380-987f69aa3bdb",
                headers={"Authorization": "Bearer valid-api-key"},
            )

        assert response.status_code == 204
        assert response.content == b""

    anyio.run(run)


def test_change_password_endpoint_returns_no_content() -> None:
    async def run() -> None:
        app = await build_identity_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.post(
                "/v1/me/password",
                headers={"Authorization": "Bearer valid-api-key"},
                json={"current_password": "old secret", "new_password": "new secret"},
            )

        assert response.status_code == 204
        assert response.content == b""

    anyio.run(run)


def test_settings_endpoint_returns_preferences_and_notifications() -> None:
    async def run() -> None:
        app = await build_identity_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get(
                "/v1/me/settings",
                headers={"Authorization": "Bearer valid-api-key"},
            )

        payload = response.json()
        assert response.status_code == 200
        assert payload["preferences"] == {
            "date_time_format": "absolute",
            "display_density": "comfortable",
            "language": "en",
            "theme": "system",
            "timezone": "UTC",
        }
        assert payload["notifications"]["security_alerts"] is True
        assert payload["public_settings"]["instance_name"] == "test-service"

    anyio.run(run)


def test_update_preferences_endpoint_returns_saved_preferences() -> None:
    async def run() -> None:
        app = await build_identity_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.patch(
                "/v1/me/preferences",
                headers={"Authorization": "Bearer valid-api-key"},
                json={
                    "date_time_format": "relative",
                    "display_density": "compact",
                    "language": "fr",
                    "theme": "dark",
                    "timezone": "Europe/Paris",
                },
            )

        assert response.status_code == 200
        assert response.json() == {
            "date_time_format": "relative",
            "display_density": "compact",
            "language": "fr",
            "theme": "dark",
            "timezone": "Europe/Paris",
        }

    anyio.run(run)


def test_update_notifications_endpoint_returns_saved_notifications() -> None:
    async def run() -> None:
        app = await build_identity_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.patch(
                "/v1/me/notifications",
                headers={"Authorization": "Bearer valid-api-key"},
                json={
                    "audit_alerts": False,
                    "email_enabled": False,
                    "in_app_enabled": True,
                    "product_updates": True,
                    "security_alerts": True,
                },
            )

        assert response.status_code == 200
        assert response.json() == {
            "audit_alerts": False,
            "email_enabled": False,
            "in_app_enabled": True,
            "product_updates": True,
            "security_alerts": True,
        }

    anyio.run(run)


def test_create_session_endpoint_sets_http_only_cookie() -> None:
    async def run() -> None:
        app = await build_identity_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.post("/v1/auth/session", json={"api_key": "valid-api-key"})

        assert response.status_code == 201
        assert response.json()["user"]["name"] == "Ada Lovelace"
        cookies = response.headers.get_list("set-cookie")
        session_cookie = next(cookie for cookie in cookies if cookie.startswith("mcp_sm_session="))
        csrf_cookie = next(cookie for cookie in cookies if cookie.startswith("mcp_sm_csrf="))
        assert "HttpOnly" in session_cookie
        assert "HttpOnly" not in csrf_cookie
        assert "valid-api-key" not in session_cookie
        assert "valid-api-key" not in csrf_cookie

    anyio.run(run)


def test_cookie_session_safe_requests_do_not_require_csrf_header() -> None:
    async def run() -> None:
        app = await build_identity_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            client.cookies.set(SESSION_COOKIE_NAME, FAKE_BROWSER_SESSION_VALUE)
            response = await client.get(
                "/v1/me/profile",
            )

        assert response.status_code == 200
        assert response.json()["email"] == "user@example.test"

    anyio.run(run)


def test_cookie_session_mutations_require_matching_csrf_header() -> None:
    async def run() -> None:
        app = await build_identity_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            client.cookies.set(SESSION_COOKIE_NAME, FAKE_BROWSER_SESSION_VALUE)
            client.cookies.set(CSRF_COOKIE_NAME, "csrf-token")
            missing = await client.patch(
                "/v1/me/profile",
                json={
                    "email": "user@example.test",
                    "name": "Ada Byron",
                    "organization": "Difference Guild",
                },
            )
            mismatch = await client.patch(
                "/v1/me/profile",
                headers={CSRF_HEADER_NAME: "wrong-token"},
                json={
                    "email": "user@example.test",
                    "name": "Ada Byron",
                    "organization": "Difference Guild",
                },
            )
            accepted = await client.patch(
                "/v1/me/profile",
                headers={CSRF_HEADER_NAME: "csrf-token"},
                json={
                    "email": "user@example.test",
                    "name": "Ada Byron",
                    "organization": "Difference Guild",
                },
            )

        assert missing.status_code == 403
        assert missing.json()["detail"] == "CSRF token is missing or invalid."
        assert mismatch.status_code == 403
        assert accepted.status_code == 200
        assert accepted.json()["name"] == "Ada Byron"

    anyio.run(run)


def test_profile_endpoint_returns_current_user_profile() -> None:
    async def run() -> None:
        app = await build_identity_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get(
                "/v1/me/profile",
                headers={"Authorization": "Bearer valid-api-key"},
            )

        payload = response.json()
        assert response.status_code == 200
        assert payload["id"] == "a6ef559c-b860-4028-a050-bb7bd2244916"
        assert payload["account_type"] == "human"
        assert payload["organization"] == "Analytical Engines"
        assert payload["permissions"]["update"] is True

    anyio.run(run)


def test_update_profile_endpoint_returns_updated_metadata() -> None:
    async def run() -> None:
        app = await build_identity_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.patch(
                "/v1/me/profile",
                headers={"Authorization": "Bearer valid-api-key"},
                json={
                    "email": "user@example.test",
                    "name": "Ada Byron",
                    "organization": "Difference Guild",
                },
            )

        payload = response.json()
        assert response.status_code == 200
        assert payload["name"] == "Ada Byron"
        assert payload["organization"] == "Difference Guild"
        assert payload["email_editable"] is False

    anyio.run(run)


def test_settings_endpoints_round_trip_preferences_and_notifications() -> None:
    async def run() -> None:
        app = await build_identity_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            settings = await client.get(
                "/v1/me/settings",
                headers={"Authorization": "Bearer valid-api-key"},
            )
            preferences = await client.patch(
                "/v1/me/preferences",
                headers={"Authorization": "Bearer valid-api-key"},
                json={
                    "date_time_format": "relative",
                    "display_density": "compact",
                    "language": "fr",
                    "theme": "dark",
                    "timezone": "Europe/Paris",
                },
            )
            notifications = await client.patch(
                "/v1/me/notifications",
                headers={"Authorization": "Bearer valid-api-key"},
                json={
                    "audit_alerts": False,
                    "email_enabled": False,
                    "in_app_enabled": True,
                    "product_updates": True,
                    "security_alerts": True,
                },
            )

        assert settings.status_code == 200
        assert settings.json()["preferences"]["theme"] == "system"
        assert settings.json()["public_settings"]["instance_name"] == "test-service"
        assert preferences.status_code == 200
        assert preferences.json()["timezone"] == "Europe/Paris"
        assert notifications.status_code == 200
        assert notifications.json()["product_updates"] is True

    anyio.run(run)


def test_active_sessions_endpoint_lists_and_revokes_sessions() -> None:
    async def run() -> None:
        app = await build_identity_app()
        transport = ASGITransport(app=app)
        session_id = "c890ab63-7337-4da3-a380-987f69aa3bdb"

        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            listed = await client.get(
                "/v1/me/sessions",
                headers={"Authorization": "Bearer valid-api-key"},
            )
            revoked = await client.delete(
                f"/v1/me/sessions/{session_id}",
                headers={"Authorization": "Bearer valid-api-key"},
            )

        assert listed.status_code == 200
        assert listed.json()["data"][0]["current"] is True
        assert "token" not in listed.json()["data"][0]
        assert revoked.status_code == 204

    anyio.run(run)


def test_api_key_middleware_injects_authenticated_identity() -> None:
    async def run() -> None:
        app = create_app(
            service_name="test-service",
            authenticate_api_key_use_case=cast(
                AuthenticateApiKeyUseCase,
                FakeAuthenticateApiKeyUseCase(),
            ),
        )

        @app.get("/protected")
        def protected(
            identity: Annotated[
                AuthenticatedIdentity,
                Depends(get_authenticated_identity),
            ],
        ) -> dict[str, str]:
            return {"id": identity.id, "type": identity.type, "api_key_id": identity.api_key_id}

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get(
                "/protected",
                headers={"Authorization": "Bearer valid-api-key"},
            )

        assert response.status_code == 200
        assert response.json()["type"] == "user"

    anyio.run(run)

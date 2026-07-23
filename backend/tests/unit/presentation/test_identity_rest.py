from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated, cast

import anyio
from fastapi import Depends, FastAPI
from httpx import ASGITransport, AsyncClient

from application.audit.dto import AuditContext
from application.identity.dto import (
    ApiKeyCreatedResponse,
    ApiKeyListResponse,
    ApiKeyPaginationResponse,
    ApiKeyPermissionsResponse,
    ApiKeyResponse,
    AuthenticatedIdentityResponse,
    CreateApiKeyRequest,
    CreateServiceAccountRequest,
    CreateSessionRequest,
    CreateUserRequest,
    CurrentSessionResponse,
    GetApiKeyRequest,
    ListApiKeysRequest,
    RevokeApiKeyRequest,
    ServiceAccountResponse,
    SessionCreatedResponse,
    UpdateApiKeyRequest,
    UserResponse,
)
from application.identity.exceptions import AuthenticationFailedError
from application.identity.use_cases import AuthenticateApiKeyUseCase
from application.rbac.dto import AuthorizationDecision, RequirePermission
from presentation.rest.app import create_app
from presentation.rest.authentication import AuthenticatedIdentity, get_authenticated_identity
from presentation.rest.dependencies import (
    get_api_key_use_case,
    get_authorize_use_case,
    get_create_api_key_use_case,
    get_create_service_account_use_case,
    get_create_session_use_case,
    get_create_user_use_case,
    get_current_session_use_case,
    get_list_api_keys_use_case,
    get_revoke_api_key_use_case,
    get_update_api_key_use_case,
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


async def build_identity_app() -> FastAPI:
    app = create_app(
        service_name="test-service",
        authenticate_api_key_use_case=cast(
            AuthenticateApiKeyUseCase,
            FakeAuthenticateApiKeyUseCase(),
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


def test_create_session_endpoint_sets_http_only_cookie() -> None:
    async def run() -> None:
        app = await build_identity_app()
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.post("/v1/auth/session", json={"api_key": "valid-api-key"})

        assert response.status_code == 201
        assert response.json()["user"]["name"] == "Ada Lovelace"
        cookie = response.headers["set-cookie"]
        assert "mcp_sm_session=" in cookie
        assert "HttpOnly" in cookie
        assert "valid-api-key" not in cookie

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

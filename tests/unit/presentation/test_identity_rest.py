from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated, cast

import anyio
from fastapi import Depends, FastAPI
from httpx import ASGITransport, AsyncClient

from application.audit.dto import AuditContext
from application.identity.dto import (
    ApiKeyCreatedResponse,
    AuthenticatedIdentityResponse,
    CreateApiKeyRequest,
    CreateServiceAccountRequest,
    CreateUserRequest,
    ServiceAccountResponse,
    UserResponse,
)
from application.identity.exceptions import AuthenticationFailedError
from application.identity.use_cases import AuthenticateApiKeyUseCase
from presentation.rest.app import create_app
from presentation.rest.authentication import AuthenticatedIdentity, get_authenticated_identity
from presentation.rest.dependencies import (
    get_create_api_key_use_case,
    get_create_service_account_use_case,
    get_create_user_use_case,
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
            key_prefix="mcp_sm_0123456789abcdef",
            owner_id=request.owner_id,
            owner_type=request.owner_type,
            expires_at=request.expires_at,
            created_at="2026-07-21T12:00:00+00:00",
        )


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


async def build_identity_app() -> FastAPI:
    app = create_app(service_name="test-service")

    async def create_user_dependency() -> AsyncIterator[FakeCreateUserUseCase]:
        yield FakeCreateUserUseCase()

    async def create_service_account_dependency() -> AsyncIterator[FakeCreateServiceAccountUseCase]:
        yield FakeCreateServiceAccountUseCase()

    async def create_api_key_dependency() -> AsyncIterator[FakeCreateApiKeyUseCase]:
        yield FakeCreateApiKeyUseCase()

    app.dependency_overrides[get_create_user_use_case] = create_user_dependency
    app.dependency_overrides[get_create_service_account_use_case] = (
        create_service_account_dependency
    )
    app.dependency_overrides[get_create_api_key_use_case] = create_api_key_dependency
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
                json={
                    "owner_id": "a6ef559c-b860-4028-a050-bb7bd2244916",
                    "owner_type": "user",
                },
            )

        payload = response.json()
        assert response.status_code == 201
        assert payload["api_key"].startswith("mcp_sm_0123456789abcdef_")
        assert payload["key_prefix"] == "mcp_sm_0123456789abcdef"
        assert "hashed_key" not in payload

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

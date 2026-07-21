from __future__ import annotations

from collections.abc import AsyncIterator
from typing import cast

import anyio
from fastapi import Depends
from httpx import ASGITransport, AsyncClient

from application.identity.dto import AuthenticatedIdentityResponse
from application.identity.use_cases import AuthenticateApiKeyUseCase
from application.rbac.dto import AuthorizationDecision, RequirePermission
from application.rbac.exceptions import AuthorizationDeniedError
from presentation.rest.app import create_app
from presentation.rest.authorization import permission_required
from presentation.rest.dependencies import get_authorize_use_case


class FakeAuthenticateApiKeyUseCase:
    async def execute(self, raw_api_key: str) -> AuthenticatedIdentityResponse:
        assert raw_api_key == "valid-api-key"
        return AuthenticatedIdentityResponse(
            id="a6ef559c-b860-4028-a050-bb7bd2244916",
            type="user",
            api_key_id="71a35966-aa7e-48af-815a-77796de636af",
        )


class AllowAuthorizeUseCase:
    def __init__(self) -> None:
        self.request: RequirePermission | None = None

    async def execute(self, request: RequirePermission) -> AuthorizationDecision:
        self.request = request
        return AuthorizationDecision(allowed=True)


class DenyAuthorizeUseCase:
    async def execute(self, request: RequirePermission) -> AuthorizationDecision:
        assert request.permission == "secret.read"
        raise AuthorizationDeniedError("Permission denied.")


def test_permission_required_allows_authorized_identity() -> None:
    async def run() -> None:
        authorize_use_case = AllowAuthorizeUseCase()
        app = create_app(
            service_name="test-service",
            authenticate_api_key_use_case=cast(
                AuthenticateApiKeyUseCase,
                FakeAuthenticateApiKeyUseCase(),
            ),
        )

        async def authorize_dependency() -> AsyncIterator[AllowAuthorizeUseCase]:
            yield authorize_use_case

        app.dependency_overrides[get_authorize_use_case] = authorize_dependency

        @app.get(
            "/protected",
            dependencies=[
                Depends(
                    permission_required(
                        permission="secret.read",
                        scope_type="project",
                        scope_id="1e423965-794a-49d5-8272-36c78dcf3e70",
                    )
                )
            ],
        )
        def protected() -> dict[str, str]:
            return {"status": "ok"}

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get(
                "/protected",
                headers={"Authorization": "Bearer valid-api-key"},
            )

        assert response.status_code == 200
        assert authorize_use_case.request == RequirePermission(
            identity_id="a6ef559c-b860-4028-a050-bb7bd2244916",
            identity_type="user",
            permission="secret.read",
            scope_type="project",
            scope_id="1e423965-794a-49d5-8272-36c78dcf3e70",
        )

    anyio.run(run)


def test_permission_required_rejects_denied_identity() -> None:
    async def run() -> None:
        app = create_app(
            service_name="test-service",
            authenticate_api_key_use_case=cast(
                AuthenticateApiKeyUseCase,
                FakeAuthenticateApiKeyUseCase(),
            ),
        )

        async def authorize_dependency() -> AsyncIterator[DenyAuthorizeUseCase]:
            yield DenyAuthorizeUseCase()

        app.dependency_overrides[get_authorize_use_case] = authorize_dependency

        @app.get(
            "/protected",
            dependencies=[
                Depends(permission_required(permission="secret.read", scope_type="global"))
            ],
        )
        def protected() -> dict[str, str]:
            return {"status": "ok"}

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get(
                "/protected",
                headers={"Authorization": "Bearer valid-api-key"},
            )

        assert response.status_code == 403
        assert response.json() == {"detail": "Forbidden."}

    anyio.run(run)

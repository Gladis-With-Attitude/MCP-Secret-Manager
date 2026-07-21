from __future__ import annotations

from collections.abc import AsyncIterator
from typing import cast

import anyio
from httpx import ASGITransport, AsyncClient

from application.audit.dto import AuditContext, AuditEventResponse, AuditQueryRequest
from application.identity.dto import AuthenticatedIdentityResponse
from application.identity.use_cases import AuthenticateApiKeyUseCase
from application.rbac.dto import AuthorizationDecision, RequirePermission
from application.rbac.exceptions import AuthorizationDeniedError
from presentation.rest.app import create_app
from presentation.rest.dependencies import get_authorize_use_case, get_list_audit_events_use_case


class FakeAuthenticateApiKeyUseCase:
    async def execute(
        self,
        raw_api_key: str,
        audit_context: AuditContext | None = None,
    ) -> AuthenticatedIdentityResponse:
        assert raw_api_key == "valid-api-key"
        assert audit_context is not None
        return AuthenticatedIdentityResponse(
            id="a6ef559c-b860-4028-a050-bb7bd2244916",
            type="user",
            api_key_id="71a35966-aa7e-48af-815a-77796de636af",
        )


class AllowAuthorizeUseCase:
    async def execute(self, request: RequirePermission) -> AuthorizationDecision:
        assert request.permission == "audit.read"
        assert request.scope_type == "global"
        return AuthorizationDecision(allowed=True)


class DenyAuthorizeUseCase:
    async def execute(self, request: RequirePermission) -> AuthorizationDecision:
        assert request.permission == "audit.read"
        raise AuthorizationDeniedError("Permission denied.")


class FakeListAuditEventsUseCase:
    def __init__(self) -> None:
        self.request: AuditQueryRequest | None = None

    async def execute(self, request: AuditQueryRequest) -> tuple[AuditEventResponse, ...]:
        self.request = request
        return (
            AuditEventResponse(
                id="b40fc39f-dbc9-4d7e-907d-d2ef0ca58d44",
                timestamp="2026-07-21T12:00:00+00:00",
                actor_id="a6ef559c-b860-4028-a050-bb7bd2244916",
                actor_type="user",
                action="secret.decrypt",
                resource_type="secret",
                resource_id="secret-1",
                result="SUCCESS",
                ip_address="127.0.0.1",
                user_agent="test-client",
                request_id="req-1",
                metadata={"version": 2},
            ),
        )


def test_list_audit_events_returns_filtered_events_when_authorized() -> None:
    async def run() -> None:
        list_use_case = FakeListAuditEventsUseCase()
        app = create_app(
            service_name="test-service",
            authenticate_api_key_use_case=cast(
                AuthenticateApiKeyUseCase,
                FakeAuthenticateApiKeyUseCase(),
            ),
        )

        async def authorize_dependency() -> AsyncIterator[AllowAuthorizeUseCase]:
            yield AllowAuthorizeUseCase()

        async def list_dependency() -> AsyncIterator[FakeListAuditEventsUseCase]:
            yield list_use_case

        app.dependency_overrides[get_authorize_use_case] = authorize_dependency
        app.dependency_overrides[get_list_audit_events_use_case] = list_dependency

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get(
                "/v1/audit?action=secret.decrypt&result=SUCCESS&limit=25",
                headers={"Authorization": "Bearer valid-api-key"},
            )

        assert response.status_code == 200
        assert response.json()[0]["action"] == "secret.decrypt"
        assert list_use_case.request == AuditQueryRequest(
            action="secret.decrypt",
            result="SUCCESS",
            limit=25,
        )

    anyio.run(run)


def test_list_audit_events_is_protected_by_rbac() -> None:
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

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get(
                "/v1/audit",
                headers={"Authorization": "Bearer valid-api-key"},
            )

        assert response.status_code == 403
        assert response.json() == {"detail": "Forbidden."}

    anyio.run(run)

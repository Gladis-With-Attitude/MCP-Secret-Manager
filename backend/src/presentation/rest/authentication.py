from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

from application.audit.dto import AuditContext
from application.identity.dto import AuthenticatedIdentityResponse
from application.identity.exceptions import AuthenticationFailedError
from application.identity.use_cases import AuthenticateApiKeyUseCase
from presentation.rest.observability import get_or_create_request_id


@dataclass(frozen=True, slots=True)
class AuthenticatedIdentity:
    id: str
    type: str
    api_key_id: str

    @classmethod
    def from_application(
        cls,
        response: AuthenticatedIdentityResponse,
    ) -> AuthenticatedIdentity:
        return cls(id=response.id, type=response.type, api_key_id=response.api_key_id)


class ApiKeyAuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        authenticate_api_key_use_case: AuthenticateApiKeyUseCase | None = None,
    ) -> None:
        super().__init__(app)
        self._authenticate_api_key_use_case = authenticate_api_key_use_case

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request.state.authenticated_identity = None
        request_id = get_or_create_request_id(request)
        authorization = request.headers.get("Authorization")
        if authorization is None:
            return await call_next(request)

        if not authorization.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid authentication credentials."},
            )

        if self._authenticate_api_key_use_case is None:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={"detail": "Authentication is not configured."},
            )

        raw_api_key = authorization.removeprefix("Bearer ").strip()
        client_host = request.client.host if request.client is not None else None
        audit_context = AuditContext(
            actor_type="anonymous",
            ip_address=client_host,
            user_agent=request.headers.get("User-Agent"),
            request_id=request_id,
        )
        try:
            authenticated = await self._authenticate_api_key_use_case.execute(
                raw_api_key,
                audit_context=audit_context,
            )
        except AuthenticationFailedError:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid authentication credentials."},
            )

        request.state.authenticated_identity = AuthenticatedIdentity.from_application(authenticated)
        return await call_next(request)


def get_optional_authenticated_identity(request: Request) -> AuthenticatedIdentity | None:
    value = getattr(request.state, "authenticated_identity", None)
    if value is None:
        return None
    if not isinstance(value, AuthenticatedIdentity):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication context is invalid.",
        )
    return value


def get_authenticated_identity(
    identity: Annotated[
        AuthenticatedIdentity | None,
        Depends(get_optional_authenticated_identity),
    ],
) -> AuthenticatedIdentity:
    if identity is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication is required.",
        )
    return identity

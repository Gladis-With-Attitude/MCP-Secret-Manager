from __future__ import annotations

import secrets
from collections.abc import Callable
from dataclasses import dataclass
from hmac import compare_digest
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp

from application.audit.dto import AuditContext
from application.identity.dto import AuthenticatedIdentityResponse
from application.identity.exceptions import AuthenticationFailedError
from application.identity.use_cases import AuthenticateApiKeyUseCase, AuthenticateSessionUseCase
from presentation.rest.observability import get_or_create_request_id

SESSION_COOKIE_NAME = "mcp_sm_session"
CSRF_COOKIE_NAME = "mcp_sm_csrf"
CSRF_HEADER_NAME = "X-CSRF-Token"
SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "TRACE"})

AuthenticateApiKeyUseCaseProvider = (
    AuthenticateApiKeyUseCase | Callable[[], AuthenticateApiKeyUseCase]
)
AuthenticateSessionUseCaseProvider = (
    AuthenticateSessionUseCase | Callable[[], AuthenticateSessionUseCase]
)


@dataclass(frozen=True, slots=True)
class AuthenticatedIdentity:
    id: str
    type: str
    api_key_id: str
    session_id: str | None = None

    @classmethod
    def from_application(
        cls,
        response: AuthenticatedIdentityResponse,
    ) -> AuthenticatedIdentity:
        return cls(
            id=response.id,
            type=response.type,
            api_key_id=response.api_key_id,
            session_id=response.session_id,
        )


class ApiKeyAuthenticationMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        authenticate_api_key_use_case: AuthenticateApiKeyUseCaseProvider | None = None,
        authenticate_session_use_case: AuthenticateSessionUseCaseProvider | None = None,
    ) -> None:
        super().__init__(app)
        self._authenticate_api_key_use_case = authenticate_api_key_use_case
        self._authenticate_session_use_case = authenticate_session_use_case

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request.state.authenticated_identity = None
        request_id = get_or_create_request_id(request)
        authorization = request.headers.get("Authorization")
        if authorization is None:
            session_token = request.cookies.get(SESSION_COOKIE_NAME)
            if session_token is None:
                return await call_next(request)
            authenticate_session_use_case = self._resolve_session_use_case()
            if authenticate_session_use_case is None:
                return JSONResponse(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    content={"detail": "Authentication is not configured."},
                )
            try:
                authenticated = await authenticate_session_use_case.execute(session_token)
            except AuthenticationFailedError:
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Invalid authentication credentials."},
                )
            request.state.authenticated_identity = AuthenticatedIdentity.from_application(
                authenticated
            )
            if not is_csrf_token_valid(request):
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "CSRF token is missing or invalid."},
                )
            return await call_next(request)

        if not authorization.startswith("Bearer "):
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Invalid authentication credentials."},
            )

        authenticate_api_key_use_case = self._resolve_api_key_use_case()
        if authenticate_api_key_use_case is None:
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
            authenticated = await authenticate_api_key_use_case.execute(
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

    def _resolve_api_key_use_case(self) -> AuthenticateApiKeyUseCase | None:
        use_case = self._authenticate_api_key_use_case
        if use_case is None:
            return None
        if callable(use_case):
            return use_case()
        return use_case

    def _resolve_session_use_case(self) -> AuthenticateSessionUseCase | None:
        use_case = self._authenticate_session_use_case
        if use_case is None:
            return None
        if callable(use_case):
            return use_case()
        return use_case


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


def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def is_csrf_token_valid(request: Request) -> bool:
    if request.method.upper() in SAFE_METHODS:
        return True

    cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
    header_token = request.headers.get(CSRF_HEADER_NAME)
    if cookie_token is None or header_token is None:
        return False

    return compare_digest(cookie_token, header_token.strip())

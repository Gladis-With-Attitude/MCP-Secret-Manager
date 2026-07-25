from __future__ import annotations

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from starlette.types import ASGIApp

from infrastructure.configuration.models import SecurityHeadersConfig

DEFAULT_SECURITY_HEADERS = SecurityHeadersConfig(
    enabled=True,
    hsts_enabled=False,
    content_security_policy="frame-ancestors 'none'; base-uri 'none'; form-action 'none'",
    frame_options="DENY",
    content_type_options="nosniff",
    referrer_policy="no-referrer",
    permissions_policy="camera=(), microphone=(), geolocation=()",
    strict_transport_security="max-age=31536000; includeSubDomains",
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: ASGIApp,
        config: SecurityHeadersConfig = DEFAULT_SECURITY_HEADERS,
    ) -> None:
        super().__init__(app)
        self._config = config

    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        response = await call_next(request)
        if self._config.enabled:
            apply_security_headers(response, self._config)
        return response


def apply_security_headers(response: Response, config: SecurityHeadersConfig) -> None:
    response.headers.setdefault("Content-Security-Policy", config.content_security_policy)
    response.headers.setdefault("X-Frame-Options", config.frame_options)
    response.headers.setdefault("X-Content-Type-Options", config.content_type_options)
    response.headers.setdefault("Referrer-Policy", config.referrer_policy)
    response.headers.setdefault("Permissions-Policy", config.permissions_policy)
    if config.hsts_enabled:
        response.headers.setdefault(
            "Strict-Transport-Security",
            config.strict_transport_security,
        )

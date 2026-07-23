from __future__ import annotations

from collections.abc import Awaitable, Callable

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse, PlainTextResponse
from starlette.types import Lifespan

from application.health import HealthStatus, get_liveness_status
from application.identity.use_cases import AuthenticateApiKeyUseCase, AuthenticateSessionUseCase
from presentation.rest.audit import router as audit_router
from presentation.rest.authentication import ApiKeyAuthenticationMiddleware
from presentation.rest.identity import router as identity_router
from presentation.rest.observability import InMemoryHttpMetrics, RequestObservabilityMiddleware
from presentation.rest.projects import router as projects_router
from presentation.rest.rbac import router as rbac_router
from presentation.rest.secrets import router as secrets_router
from presentation.rest.vaults import router as vaults_router


def create_app(
    service_name: str = "mcp-secret-manager",
    openapi_enabled: bool = True,
    lifespan: Lifespan[FastAPI] | None = None,
    authenticate_api_key_use_case: AuthenticateApiKeyUseCase | None = None,
    authenticate_session_use_case: AuthenticateSessionUseCase | None = None,
    health_check: Callable[[], Awaitable[HealthStatus]] | None = None,
) -> FastAPI:
    docs_url = "/docs" if openapi_enabled else None
    openapi_url = "/openapi.json" if openapi_enabled else None
    app = FastAPI(
        title="MCP Secret Manager",
        version="0.1.0",
        docs_url=docs_url,
        redoc_url=None,
        openapi_url=openapi_url,
        lifespan=lifespan,
    )

    @app.exception_handler(RequestValidationError)
    async def request_validation_handler(
        _request: object,
        _exc: RequestValidationError,
    ) -> JSONResponse:
        return JSONResponse(
            status_code=400,
            content={"detail": "Invalid request data."},
        )

    @app.get("/v1/health", tags=["health"])
    async def health() -> dict[str, str]:
        status = (
            await health_check() if health_check is not None else get_liveness_status(service_name)
        )
        return status.as_public_dict()

    metrics = InMemoryHttpMetrics()
    app.state.metrics = metrics

    @app.get("/v1/metrics", tags=["observability"], response_class=PlainTextResponse)
    async def metrics_endpoint() -> str:
        return metrics.render_prometheus()

    app.include_router(vaults_router)
    app.include_router(projects_router)
    app.include_router(secrets_router)
    app.include_router(identity_router)
    app.include_router(rbac_router)
    app.include_router(audit_router)
    app.add_middleware(
        ApiKeyAuthenticationMiddleware,
        authenticate_api_key_use_case=authenticate_api_key_use_case,
        authenticate_session_use_case=authenticate_session_use_case,
    )
    app.add_middleware(RequestObservabilityMiddleware, metrics=metrics)

    return app


app = create_app()

from __future__ import annotations

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.types import Lifespan

from application.health import get_liveness_status
from presentation.rest.vaults import router as vaults_router


def create_app(
    service_name: str = "mcp-secret-manager",
    openapi_enabled: bool = True,
    lifespan: Lifespan[FastAPI] | None = None,
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
    def health() -> dict[str, str]:
        status = get_liveness_status(service_name)
        return status.as_public_dict()

    app.include_router(vaults_router)

    return app


app = create_app()

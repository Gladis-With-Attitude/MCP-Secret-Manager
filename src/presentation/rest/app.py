from __future__ import annotations

from fastapi import FastAPI

from application.health import get_liveness_status
from infrastructure.config import AppSettings, get_settings


def create_app(settings: AppSettings | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()
    resolved_settings.validate_runtime()

    docs_url = "/docs" if resolved_settings.openapi_enabled else None
    openapi_url = "/openapi.json" if resolved_settings.openapi_enabled else None

    app = FastAPI(
        title="MCP Secret Manager",
        version="0.1.0",
        docs_url=docs_url,
        redoc_url=None,
        openapi_url=openapi_url,
    )

    @app.get("/v1/health", tags=["health"])
    def health() -> dict[str, str]:
        status = get_liveness_status(resolved_settings.service_name)
        return status.as_public_dict()

    return app


app = create_app()

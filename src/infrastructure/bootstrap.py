from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from application.project.use_cases import CreateProjectUseCase
from application.secret.use_cases import CreateSecretUseCase
from application.vault.use_cases import CreateVaultUseCase
from infrastructure.config import AppSettings, get_settings
from infrastructure.persistence.database import create_database_engine, create_session_factory
from infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork
from presentation.rest.app import create_app
from presentation.rest.dependencies import (
    get_create_project_use_case,
    get_create_secret_use_case,
    get_create_vault_use_case,
)


def create_rest_app(settings: AppSettings | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()
    resolved_settings.validate_runtime()

    engine = (
        create_database_engine(resolved_settings.database_url)
        if resolved_settings.database_url is not None
        else None
    )
    session_factory = create_session_factory(engine) if engine is not None else None

    @asynccontextmanager
    async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
        try:
            yield
        finally:
            if engine is not None:
                await engine.dispose()

    app = create_app(
        service_name=resolved_settings.service_name,
        openapi_enabled=resolved_settings.openapi_enabled,
        lifespan=lifespan,
    )

    if session_factory is not None:

        def create_vault_use_case() -> CreateVaultUseCase:
            return CreateVaultUseCase(SqlAlchemyUnitOfWork(session_factory))

        def create_project_use_case() -> CreateProjectUseCase:
            return CreateProjectUseCase(SqlAlchemyUnitOfWork(session_factory))

        def create_secret_use_case() -> CreateSecretUseCase:
            return CreateSecretUseCase(SqlAlchemyUnitOfWork(session_factory))

        app.dependency_overrides[get_create_vault_use_case] = create_vault_use_case
        app.dependency_overrides[get_create_project_use_case] = create_project_use_case
        app.dependency_overrides[get_create_secret_use_case] = create_secret_use_case

    return app


app = create_rest_app()

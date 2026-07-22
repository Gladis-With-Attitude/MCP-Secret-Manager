from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, cast

import anyio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from infrastructure import bootstrap
from infrastructure.config import AppSettings
from presentation.rest.dependencies import (
    get_active_secret_version_use_case,
    get_authorize_use_case,
    get_create_api_key_use_case,
    get_create_project_use_case,
    get_create_secret_use_case,
    get_create_secret_version_use_case,
    get_create_service_account_use_case,
    get_create_user_use_case,
    get_create_vault_use_case,
    get_list_audit_events_use_case,
    get_list_secret_versions_use_case,
)


class FakeConnection:
    async def __aenter__(self) -> FakeConnection:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: object | None,
    ) -> None:
        return None

    async def execute(self, _statement: object) -> None:
        return None


class FakeEngine:
    def __init__(self) -> None:
        self.disposed = False

    def connect(self) -> FakeConnection:
        return FakeConnection()

    async def dispose(self) -> None:
        self.disposed = True


def create_bootstrapped_app(monkeypatch: Any) -> tuple[FastAPI, FakeEngine]:
    fake_engine = FakeEngine()
    fake_session_factory = cast(async_sessionmaker[AsyncSession], object())

    monkeypatch.setattr(
        bootstrap,
        "create_database_engine",
        lambda _database_url: cast(AsyncEngine, fake_engine),
    )
    monkeypatch.setattr(
        bootstrap,
        "create_session_factory",
        lambda _engine: fake_session_factory,
    )

    settings = AppSettings(
        environment="development",
        database_url="postgresql+asyncpg://user:password@postgres:5432/app",
        master_key_base64="MDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDA=",
        service_name="test-service",
        bootstrap_admin_email="admin@example.local",
        bootstrap_admin_name="Administrator",
    )

    return bootstrap.create_rest_app(settings), fake_engine


def test_bootstrapped_rest_app_injects_all_existing_rest_dependencies(monkeypatch: Any) -> None:
    app, _fake_engine = create_bootstrapped_app(monkeypatch)

    expected_overrides = {
        get_active_secret_version_use_case,
        get_authorize_use_case,
        get_create_api_key_use_case,
        get_create_project_use_case,
        get_create_secret_use_case,
        get_create_secret_version_use_case,
        get_create_service_account_use_case,
        get_create_user_use_case,
        get_create_vault_use_case,
        get_list_audit_events_use_case,
        get_list_secret_versions_use_case,
    }

    assert expected_overrides.issubset(app.dependency_overrides)


def test_bootstrapped_health_reports_runtime_dependencies(monkeypatch: Any) -> None:
    async def run() -> None:
        app, _fake_engine = create_bootstrapped_app(monkeypatch)
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            response = await client.get("/v1/health")

        assert response.status_code == 200
        assert response.json() == {
            "status": "ok",
            "service": "test-service",
            "api": "ok",
            "configuration": "ok",
            "database": "ok",
            "repositories": "ok",
            "use_cases": "ok",
        }

    anyio.run(run)


def test_bootstrapped_lifespan_opens_and_closes_runtime(monkeypatch: Any) -> None:
    async def run() -> None:
        app, fake_engine = create_bootstrapped_app(monkeypatch)

        @asynccontextmanager
        async def lifespan_context() -> AsyncIterator[None]:
            async with app.router.lifespan_context(app):
                yield

        async with lifespan_context():
            assert fake_engine.disposed is False

        assert fake_engine.disposed is True

    anyio.run(run)

from __future__ import annotations

import asyncio
import os
import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine

from domain.rbac.permissions import DEFAULT_PERMISSIONS
from infrastructure import database_migrations
from infrastructure.config import AppSettings
from infrastructure.persistence.database import create_database_engine, create_session_factory
from infrastructure.seed.orchestrator import SeedOrchestrator
from infrastructure.seed.settings import SeedSettings

ADMIN_API_KEY = "mcp_sm_0123456789abcdef_" + ("a" * 64)
HEAD_REVISION = "0014_create_user_preferences"


def quote_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def render_database_url(database_url: str, database_name: str) -> str:
    url = make_url(database_url)
    return url.set(database=database_name).render_as_string(hide_password=False)


@pytest.fixture
def database_url() -> str:
    value = os.environ.get("MCP_SECRET_MANAGER_TEST_DATABASE_URL")
    if value is None:
        pytest.skip("MCP_SECRET_MANAGER_TEST_DATABASE_URL is required for seed tests.")
    return value


@pytest.fixture
def alembic_config_path() -> str:
    try:
        return str(database_migrations.find_alembic_config())
    except RuntimeError as exc:
        pytest.skip(str(exc))


async def create_database(admin_database_url: str, database_name: str) -> None:
    engine = create_async_engine(admin_database_url, isolation_level="AUTOCOMMIT")
    try:
        async with engine.connect() as connection:
            await connection.execute(text(f"CREATE DATABASE {quote_identifier(database_name)}"))
    finally:
        await engine.dispose()


async def drop_database(admin_database_url: str, database_name: str) -> None:
    engine = create_async_engine(admin_database_url, isolation_level="AUTOCOMMIT")
    try:
        async with engine.connect() as connection:
            await connection.execute(
                text(f"DROP DATABASE IF EXISTS {quote_identifier(database_name)} WITH (FORCE)")
            )
    finally:
        await engine.dispose()


async def scalar(database_url: str, statement: str) -> int | str:
    engine = create_async_engine(database_url)
    try:
        async with engine.connect() as connection:
            value = (await connection.execute(text(statement))).scalar_one()
            if not isinstance(value, (int, str)):
                msg = "Unexpected scalar value."
                raise TypeError(msg)
            return value
    finally:
        await engine.dispose()


async def run_seed(database_url: str) -> None:
    settings = SeedSettings.from_app_settings(
        AppSettings(
            environment="test",
            database_url=database_url,
            bootstrap_admin_email="admin@example.local",
            bootstrap_admin_name="Administrator",
            bootstrap_admin_api_key=ADMIN_API_KEY,
        )
    )
    engine = create_database_engine(database_url)
    try:
        await SeedOrchestrator(create_session_factory(engine)).run(settings)
    finally:
        await engine.dispose()


@pytest.mark.integration
def test_seed_bootstrap_is_idempotent_on_postgresql_database(
    database_url: str,
    alembic_config_path: str,
) -> None:
    database_name = f"mcp_secret_manager_seed_test_{uuid.uuid4().hex}"
    seeded_database_url = render_database_url(database_url, database_name)
    settings = AppSettings(environment="test", database_url=seeded_database_url)

    asyncio.run(create_database(database_url, database_name))
    try:
        database_migrations.upgrade(settings=settings, config_path=alembic_config_path)

        asyncio.run(run_seed(seeded_database_url))
        asyncio.run(run_seed(seeded_database_url))

        assert asyncio.run(scalar(seeded_database_url, "SELECT count(*) FROM permissions")) == len(
            DEFAULT_PERMISSIONS
        )
        assert asyncio.run(scalar(seeded_database_url, "SELECT count(*) FROM roles")) == 3
        assert asyncio.run(scalar(seeded_database_url, "SELECT count(*) FROM users")) == 1
        assert asyncio.run(scalar(seeded_database_url, "SELECT count(*) FROM api_keys")) == 1
        assert (
            asyncio.run(scalar(seeded_database_url, "SELECT count(*) FROM role_assignments")) == 1
        )
        assert (
            asyncio.run(scalar(seeded_database_url, "SELECT version_num FROM alembic_version"))
            == HEAD_REVISION
        )
    finally:
        asyncio.run(drop_database(database_url, database_name))

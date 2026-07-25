from __future__ import annotations

import asyncio
import os
import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine

from infrastructure import database_migrations
from infrastructure.config import AppSettings

HEAD_REVISION = "0014_create_user_preferences"
PREVIOUS_REVISION = "0013_add_api_key_metadata"


def quote_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def render_database_url(database_url: str, database_name: str) -> str:
    url = make_url(database_url)
    return url.set(database=database_name).render_as_string(hide_password=False)


@pytest.fixture
def database_url() -> str:
    value = os.environ.get("MCP_SECRET_MANAGER_TEST_DATABASE_URL")
    if value is None:
        pytest.skip("MCP_SECRET_MANAGER_TEST_DATABASE_URL is required for migration tests.")
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


async def current_revision(database_url: str) -> str:
    engine = create_async_engine(database_url)
    try:
        async with engine.connect() as connection:
            result = await connection.execute(text("SELECT version_num FROM alembic_version"))
            value = result.scalar_one()
            if not isinstance(value, str):
                msg = "Alembic version is not a string."
                raise TypeError(msg)
            return value
    finally:
        await engine.dispose()


@pytest.mark.integration
def test_migration_lifecycle_on_empty_postgresql_database(
    database_url: str,
    alembic_config_path: str,
) -> None:
    database_name = f"mcp_secret_manager_migration_test_{uuid.uuid4().hex}"
    migrated_database_url = render_database_url(database_url, database_name)
    settings = AppSettings(environment="test", database_url=migrated_database_url)

    asyncio.run(create_database(database_url, database_name))
    try:
        database_migrations.upgrade(settings=settings, config_path=alembic_config_path)
        assert asyncio.run(current_revision(migrated_database_url)) == HEAD_REVISION

        database_migrations.upgrade(settings=settings, config_path=alembic_config_path)
        assert asyncio.run(current_revision(migrated_database_url)) == HEAD_REVISION

        database_migrations.downgrade(
            "-1",
            settings=settings,
            config_path=alembic_config_path,
        )
        assert asyncio.run(current_revision(migrated_database_url)) == PREVIOUS_REVISION

        database_migrations.upgrade(settings=settings, config_path=alembic_config_path)
        assert asyncio.run(current_revision(migrated_database_url)) == HEAD_REVISION
    finally:
        asyncio.run(drop_database(database_url, database_name))

from __future__ import annotations

import os
from collections.abc import AsyncIterator

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from domain.identity.entities import User, UserPreferences
from domain.identity.value_objects import UserDisplayName, UserEmail
from infrastructure.persistence import Base
from infrastructure.persistence.identity_repositories import (
    SqlAlchemyUserPreferencesRepository,
    SqlAlchemyUserRepository,
)

TEST_SCHEMA = "mcp_secret_manager_identity_preferences_repository_test"


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
def database_url() -> str:
    value = os.environ.get("MCP_SECRET_MANAGER_TEST_DATABASE_URL")
    if value is None:
        pytest.skip("MCP_SECRET_MANAGER_TEST_DATABASE_URL is required for PostgreSQL tests.")
    return value


@pytest.fixture
async def session_factory(
    database_url: str,
) -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    admin_engine = create_async_engine(database_url, isolation_level="AUTOCOMMIT")
    async with admin_engine.begin() as connection:
        await connection.execute(text(f'DROP SCHEMA IF EXISTS "{TEST_SCHEMA}" CASCADE'))
        await connection.execute(text(f'CREATE SCHEMA "{TEST_SCHEMA}"'))
    await admin_engine.dispose()

    engine = create_async_engine(
        database_url,
        connect_args={"server_settings": {"search_path": TEST_SCHEMA}},
    )
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    try:
        yield async_sessionmaker(engine, expire_on_commit=False)
    finally:
        await engine.dispose()
        cleanup_engine = create_async_engine(database_url, isolation_level="AUTOCOMMIT")
        async with cleanup_engine.begin() as connection:
            await connection.execute(text(f'DROP SCHEMA IF EXISTS "{TEST_SCHEMA}" CASCADE'))
        await cleanup_engine.dispose()


@pytest.mark.integration
@pytest.mark.anyio
async def test_user_preferences_repository_upserts_profile_and_settings(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        user = await SqlAlchemyUserRepository(session).create(
            User.create(
                email=UserEmail("preferences@example.test"),
                display_name=UserDisplayName("Preferences User"),
            )
        )
        repository = SqlAlchemyUserPreferencesRepository(session)
        created = await repository.upsert(UserPreferences.default(user.id))
        updated = await repository.upsert(
            created.update_profile_metadata(organization="Analytical Engines").update_preferences(
                theme="dark",
                language="fr",
                timezone="Europe/Paris",
                date_time_format="relative",
                display_density="compact",
            )
        )
        await session.commit()

    async with session_factory() as session:
        fetched = await SqlAlchemyUserPreferencesRepository(session).get(user.id)

    assert fetched is not None
    assert fetched.organization == "Analytical Engines"
    assert fetched.theme == updated.theme == "dark"
    assert fetched.language == "fr"
    assert fetched.timezone == "Europe/Paris"

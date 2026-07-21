from __future__ import annotations

import os
from collections.abc import AsyncIterator

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from domain.project.entities import Project
from domain.project.repositories import ProjectRepositoryConflictError
from domain.project.value_objects import ProjectName
from domain.vault.entities import Vault
from domain.vault.value_objects import VaultName
from infrastructure.persistence import Base
from infrastructure.persistence.project_repository import SqlAlchemyProjectRepository
from infrastructure.persistence.vault_repository import SqlAlchemyVaultRepository

TEST_SCHEMA = "mcp_secret_manager_project_repository_test"


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


async def create_vault(
    session: AsyncSession,
    name: str,
) -> Vault:
    repository = SqlAlchemyVaultRepository(session)
    return await repository.create(Vault.create(VaultName(name)))


@pytest.mark.integration
@pytest.mark.anyio
async def test_project_repository_create_get_list_and_exists(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        vault = await create_vault(session, "Production")
        repository = SqlAlchemyProjectRepository(session)
        project = Project.create(vault_id=vault.id, name=ProjectName("API"))

        created = await repository.create(project)
        await session.commit()

    async with session_factory() as session:
        repository = SqlAlchemyProjectRepository(session)

        fetched = await repository.get(created.id)
        listed = await repository.list_by_vault(vault.id)
        exists = await repository.exists_in_vault(vault.id, ProjectName("API"))

    assert fetched == created
    assert listed == (created,)
    assert exists is True


@pytest.mark.integration
@pytest.mark.anyio
async def test_project_repository_enforces_unique_name_per_vault(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        vault = await create_vault(session, "Production")
        repository = SqlAlchemyProjectRepository(session)
        await repository.create(Project.create(vault_id=vault.id, name=ProjectName("API")))

        with pytest.raises(ProjectRepositoryConflictError):
            await repository.create(Project.create(vault_id=vault.id, name=ProjectName("API")))


@pytest.mark.integration
@pytest.mark.anyio
async def test_project_repository_allows_same_name_in_different_vaults(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        first_vault = await create_vault(session, "Production")
        second_vault = await create_vault(session, "Development")
        repository = SqlAlchemyProjectRepository(session)

        first_project = await repository.create(
            Project.create(vault_id=first_vault.id, name=ProjectName("API"))
        )
        second_project = await repository.create(
            Project.create(vault_id=second_vault.id, name=ProjectName("API"))
        )

    assert first_project.name == second_project.name
    assert first_project.vault_id != second_project.vault_id


@pytest.mark.integration
@pytest.mark.anyio
async def test_project_repository_requires_existing_vault(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        repository = SqlAlchemyProjectRepository(session)

        with pytest.raises(ProjectRepositoryConflictError):
            await repository.create(
                Project.create(
                    vault_id=Vault.create(VaultName("Ghost")).id,
                    name=ProjectName("API"),
                )
            )

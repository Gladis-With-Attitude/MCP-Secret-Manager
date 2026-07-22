from __future__ import annotations

import os
from collections.abc import AsyncIterator
from datetime import UTC, datetime

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from domain.project.entities import Project
from domain.project.value_objects import ProjectName
from domain.secret.entities import Secret
from domain.secret.repositories import SecretRepositoryConflictError
from domain.secret.value_objects import SecretDescription, SecretKey
from domain.vault.entities import Vault
from domain.vault.value_objects import VaultName
from infrastructure.persistence import Base
from infrastructure.persistence.project_repository import SqlAlchemyProjectRepository
from infrastructure.persistence.secret_model import SecretModel
from infrastructure.persistence.secret_repository import SqlAlchemySecretRepository
from infrastructure.persistence.vault_repository import SqlAlchemyVaultRepository

TEST_SCHEMA = "mcp_secret_manager_secret_repository_test"


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


async def create_project(session: AsyncSession, name: str) -> Project:
    vault_repository = SqlAlchemyVaultRepository(session)
    project_repository = SqlAlchemyProjectRepository(session)
    vault = await vault_repository.create(Vault.create(VaultName(f"{name} Vault")))
    return await project_repository.create(Project.create(vault.id, ProjectName(name)))


@pytest.mark.integration
@pytest.mark.anyio
async def test_secret_repository_create_get_list_and_exists(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        project = await create_project(session, "API")
        repository = SqlAlchemySecretRepository(session)
        secret = Secret.create(
            project_id=project.id,
            key=SecretKey("OPENAI_API_KEY"),
            description=SecretDescription("OpenAI API key metadata."),
        )

        created = await repository.create(secret)
        await session.commit()

    async with session_factory() as session:
        repository = SqlAlchemySecretRepository(session)

        fetched = await repository.get(created.id)
        listed = await repository.list_by_project(project.id)
        exists = await repository.exists_in_project(project.id, SecretKey("OPENAI_API_KEY"))

    assert fetched == created
    assert listed == (created,)
    assert exists is True
    assert fetched is not None
    assert fetched.description.value == "OpenAI API key metadata."


@pytest.mark.integration
@pytest.mark.anyio
async def test_secret_repository_enforces_unique_key_per_project(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        project = await create_project(session, "API")
        repository = SqlAlchemySecretRepository(session)
        await repository.create(
            Secret.create(
                project_id=project.id,
                key=SecretKey("OPENAI_API_KEY"),
                description=SecretDescription(None),
            )
        )

        with pytest.raises(SecretRepositoryConflictError):
            await repository.create(
                Secret.create(
                    project_id=project.id,
                    key=SecretKey("OPENAI_API_KEY"),
                    description=SecretDescription(None),
                )
            )


@pytest.mark.integration
@pytest.mark.anyio
async def test_secret_repository_allows_same_key_in_different_projects(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        first_project = await create_project(session, "API")
        second_project = await create_project(session, "Worker")
        repository = SqlAlchemySecretRepository(session)

        first_secret = await repository.create(
            Secret.create(
                project_id=first_project.id,
                key=SecretKey("OPENAI_API_KEY"),
                description=SecretDescription(None),
            )
        )
        second_secret = await repository.create(
            Secret.create(
                project_id=second_project.id,
                key=SecretKey("OPENAI_API_KEY"),
                description=SecretDescription(None),
            )
        )

    assert first_secret.key == second_secret.key
    assert first_secret.project_id != second_secret.project_id


@pytest.mark.integration
@pytest.mark.anyio
async def test_secret_repository_requires_existing_project(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        repository = SqlAlchemySecretRepository(session)
        ghost_project = Project.create(
            vault_id=Vault.create(VaultName("Ghost")).id,
            name=ProjectName("API"),
        )

        with pytest.raises(SecretRepositoryConflictError):
            await repository.create(
                Secret.create(
                    project_id=ghost_project.id,
                    key=SecretKey("OPENAI_API_KEY"),
                    description=SecretDescription(None),
                )
            )


@pytest.mark.integration
@pytest.mark.anyio
async def test_secret_table_enforces_key_format_check(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        project = await create_project(session, "API")
        secret = Secret.create(
            project_id=project.id,
            key=SecretKey("OPENAI_API_KEY"),
            description=SecretDescription(None),
        )
        session.add(
            SecretModel(
                id=secret.id.value,
                project_id=project.id.value,
                key="openai-api-key",
                description=None,
                type="generic",
                metadata_json={},
                tags=[],
                archived=False,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
                archived_at=None,
            )
        )

        with pytest.raises(IntegrityError):
            await session.flush()

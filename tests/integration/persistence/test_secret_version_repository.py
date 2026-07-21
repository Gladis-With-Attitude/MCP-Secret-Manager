from __future__ import annotations

import os
from collections.abc import AsyncIterator

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from domain.project.entities import Project
from domain.project.value_objects import ProjectName
from domain.secret.entities import Secret
from domain.secret.value_objects import SecretDescription, SecretKey
from domain.secret_version.entities import SecretVersion
from domain.secret_version.repositories import SecretVersionRepositoryConflictError
from domain.secret_version.value_objects import (
    SecretValue,
    SecretVersionId,
    SecretVersionNumber,
)
from domain.vault.entities import Vault
from domain.vault.value_objects import VaultName
from infrastructure.persistence import Base
from infrastructure.persistence.project_repository import SqlAlchemyProjectRepository
from infrastructure.persistence.secret_repository import SqlAlchemySecretRepository
from infrastructure.persistence.secret_version_model import SecretVersionModel
from infrastructure.persistence.secret_version_repository import SqlAlchemySecretVersionRepository
from infrastructure.persistence.vault_repository import SqlAlchemyVaultRepository

TEST_SCHEMA = "mcp_secret_manager_secret_version_repository_test"


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


async def create_secret(session: AsyncSession, name: str = "API") -> Secret:
    vault_repository = SqlAlchemyVaultRepository(session)
    project_repository = SqlAlchemyProjectRepository(session)
    secret_repository = SqlAlchemySecretRepository(session)
    vault = await vault_repository.create(Vault.create(VaultName(f"{name} Vault")))
    project = await project_repository.create(Project.create(vault.id, ProjectName(name)))
    return await secret_repository.create(
        Secret.create(
            project_id=project.id,
            key=SecretKey("OPENAI_API_KEY"),
            description=SecretDescription(None),
        )
    )


@pytest.mark.integration
@pytest.mark.anyio
async def test_secret_version_repository_create_get_list_and_active(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        secret = await create_secret(session)
        repository = SqlAlchemySecretVersionRepository(session)
        secret_version = SecretVersion.create(
            secret_id=secret.id,
            value=SecretValue("plain-value-v1"),
            version=SecretVersionNumber(1),
        )

        created = await repository.create(secret_version)
        await session.commit()

    async with session_factory() as session:
        repository = SqlAlchemySecretVersionRepository(session)

        fetched = await repository.get(created.id)
        listed = await repository.list_versions(secret.id)
        active = await repository.get_active(secret.id)

    assert fetched == created
    assert listed == (created,)
    assert active == created
    assert fetched is not None
    assert fetched.value.value == "plain-value-v1"


@pytest.mark.integration
@pytest.mark.anyio
async def test_secret_version_repository_deactivates_previous_versions(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        secret = await create_secret(session)
        repository = SqlAlchemySecretVersionRepository(session)
        first = await repository.create(
            SecretVersion.create(
                secret_id=secret.id,
                value=SecretValue("plain-value-v1"),
                version=SecretVersionNumber(1),
            )
        )
        await repository.deactivate_previous_versions(secret.id)
        second = await repository.create(
            SecretVersion.create(
                secret_id=secret.id,
                value=SecretValue("plain-value-v2"),
                version=SecretVersionNumber(2),
            )
        )
        await session.commit()

    async with session_factory() as session:
        repository = SqlAlchemySecretVersionRepository(session)
        history = await repository.list_versions(secret.id)
        active = await repository.get_active(secret.id)

    assert [version.id for version in history] == [first.id, second.id]
    assert [version.active for version in history] == [False, True]
    assert [version.value.value for version in history] == [
        "plain-value-v1",
        "plain-value-v2",
    ]
    assert active == second


@pytest.mark.integration
@pytest.mark.anyio
async def test_secret_version_repository_enforces_single_active_version(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        secret = await create_secret(session)
        repository = SqlAlchemySecretVersionRepository(session)
        await repository.create(
            SecretVersion.create(
                secret_id=secret.id,
                value=SecretValue("plain-value-v1"),
                version=SecretVersionNumber(1),
            )
        )

        with pytest.raises(SecretVersionRepositoryConflictError):
            await repository.create(
                SecretVersion.create(
                    secret_id=secret.id,
                    value=SecretValue("plain-value-v2"),
                    version=SecretVersionNumber(2),
                )
            )


@pytest.mark.integration
@pytest.mark.anyio
async def test_secret_version_repository_enforces_unique_version_per_secret(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        secret = await create_secret(session)
        repository = SqlAlchemySecretVersionRepository(session)
        first = await repository.create(
            SecretVersion.create(
                secret_id=secret.id,
                value=SecretValue("plain-value-v1"),
                version=SecretVersionNumber(1),
            )
        )
        await repository.deactivate_previous_versions(secret.id)

        with pytest.raises(SecretVersionRepositoryConflictError):
            await repository.create(
                SecretVersion(
                    id=SecretVersionId.new(),
                    secret_id=secret.id,
                    value=SecretValue("plain-value-v1-duplicate"),
                    version=SecretVersionNumber(1),
                    active=True,
                    created_at=first.created_at,
                )
            )


@pytest.mark.integration
@pytest.mark.anyio
async def test_secret_version_repository_requires_existing_secret(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        repository = SqlAlchemySecretVersionRepository(session)
        ghost_secret = Secret.create(
            project_id=Project.create(
                vault_id=Vault.create(VaultName("Ghost Vault")).id,
                name=ProjectName("API"),
            ).id,
            key=SecretKey("OPENAI_API_KEY"),
            description=SecretDescription(None),
        )

        with pytest.raises(SecretVersionRepositoryConflictError):
            await repository.create(
                SecretVersion.create(
                    secret_id=ghost_secret.id,
                    value=SecretValue("plain-value"),
                    version=SecretVersionNumber(1),
                )
            )


@pytest.mark.integration
@pytest.mark.anyio
async def test_secret_version_table_enforces_required_value_check(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        secret = await create_secret(session)
        secret_version = SecretVersion.create(
            secret_id=secret.id,
            value=SecretValue("plain-value-v1"),
            version=SecretVersionNumber(1),
        )
        session.add(
            SecretVersionModel(
                id=secret_version.id.value,
                secret_id=secret.id.value,
                value="",
                version=secret_version.version.value,
                active=True,
                created_at=secret_version.created_at,
            )
        )

        with pytest.raises(IntegrityError):
            await session.flush()

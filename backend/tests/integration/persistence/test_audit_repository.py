from __future__ import annotations

import os
from collections.abc import AsyncIterator
from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from domain.audit.entities import AuditEvent
from domain.audit.repositories import AuditEventFilter
from domain.audit.value_objects import (
    AuditAction,
    AuditActorType,
    AuditResourceType,
    AuditResult,
)
from infrastructure.persistence import Base
from infrastructure.persistence.audit_repository import SqlAlchemyAuditRepository

TEST_SCHEMA = "mcp_secret_manager_audit_repository_test"


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


def build_event(
    action: str,
    resource_id: str,
    result: AuditResult = AuditResult.SUCCESS,
) -> AuditEvent:
    return AuditEvent.create(
        actor_id="actor-1",
        actor_type=AuditActorType("user"),
        action=AuditAction(action),
        resource_type=AuditResourceType("secret"),
        resource_id=resource_id,
        result=result,
        ip_address="127.0.0.1",
        user_agent="test-client",
        request_id="req-1",
        metadata={"resource_id": resource_id},
    )


@pytest.mark.integration
@pytest.mark.anyio
async def test_audit_repository_persists_and_filters_events(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        repository = SqlAlchemyAuditRepository(session)
        first_event = build_event("secret.decrypt", "secret-1")
        second_event = build_event("secret.decrypt", "secret-2", AuditResult.FAILURE)
        third_event = build_event("secret.rotate", "secret-3")
        object.__setattr__(first_event, "timestamp", datetime(2026, 7, 21, 12, 0, tzinfo=UTC))
        object.__setattr__(second_event, "timestamp", datetime(2026, 7, 21, 12, 1, tzinfo=UTC))
        object.__setattr__(third_event, "timestamp", datetime(2026, 7, 21, 12, 2, tzinfo=UTC))
        await repository.create(first_event)
        second = await repository.create(second_event)
        await repository.create(third_event)
        await session.commit()

    async with session_factory() as session:
        repository = SqlAlchemyAuditRepository(session)
        events = await repository.search(
            AuditEventFilter(
                actor_id="actor-1",
                action=AuditAction("secret.decrypt"),
                resource_type=AuditResourceType("secret"),
                result=AuditResult.FAILURE,
            )
        )

    assert events == (second,)


@pytest.mark.integration
@pytest.mark.anyio
async def test_audit_repository_gets_event_by_id(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        repository = SqlAlchemyAuditRepository(session)
        created = await repository.create(build_event("secret.decrypt", "secret-1"))
        await session.commit()

    async with session_factory() as session:
        repository = SqlAlchemyAuditRepository(session)
        found = await repository.get(created.id)

    assert found == created


@pytest.mark.integration
@pytest.mark.anyio
async def test_audit_repository_searches_text_query(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        repository = SqlAlchemyAuditRepository(session)
        prod_event = build_event("secret.decrypt", "secret-prod-1")
        dev_event = build_event("secret.decrypt", "secret-dev-1")
        await repository.create(prod_event)
        await repository.create(dev_event)
        await session.commit()

    async with session_factory() as session:
        repository = SqlAlchemyAuditRepository(session)
        events = await repository.search(AuditEventFilter(query="prod"))

    assert tuple(event.resource_id for event in events) == ("secret-prod-1",)


@pytest.mark.integration
@pytest.mark.anyio
async def test_audit_repository_returns_events_in_chronological_order(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        repository = SqlAlchemyAuditRepository(session)
        later = build_event("secret.decrypt", "later")
        earlier = build_event("secret.decrypt", "earlier")
        object.__setattr__(later, "timestamp", datetime(2026, 7, 21, 12, 2, tzinfo=UTC))
        object.__setattr__(earlier, "timestamp", datetime(2026, 7, 21, 12, 1, tzinfo=UTC))
        await repository.create(later)
        await repository.create(earlier)
        await session.commit()

    async with session_factory() as session:
        repository = SqlAlchemyAuditRepository(session)
        events = await repository.search(AuditEventFilter(action=AuditAction("secret.decrypt")))

    assert tuple(event.resource_id for event in events) == ("earlier", "later")


@pytest.mark.integration
@pytest.mark.anyio
async def test_audit_repository_deletes_events_older_than_cutoff(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    async with session_factory() as session:
        repository = SqlAlchemyAuditRepository(session)
        old_event = build_event("secret.decrypt", "old")
        fresh_event = build_event("secret.decrypt", "fresh")
        object.__setattr__(old_event, "timestamp", datetime(2026, 1, 1, tzinfo=UTC))
        object.__setattr__(fresh_event, "timestamp", datetime(2026, 7, 21, tzinfo=UTC))
        await repository.create(old_event)
        await repository.create(fresh_event)
        deleted_count = await repository.delete_older_than(
            datetime(2026, 7, 21, tzinfo=UTC) - timedelta(days=30)
        )
        await session.commit()

    async with session_factory() as session:
        repository = SqlAlchemyAuditRepository(session)
        events = await repository.search(AuditEventFilter())

    assert deleted_count == 1
    assert tuple(event.resource_id for event in events) == ("fresh",)

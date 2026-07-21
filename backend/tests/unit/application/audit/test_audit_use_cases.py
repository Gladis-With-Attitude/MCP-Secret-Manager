from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from types import TracebackType
from typing import Self

import anyio

from application.audit.dto import AuditContext, AuditQueryRequest
from application.audit.use_cases import (
    ListAuditEventsUseCase,
    PersistentAuditRecorder,
    PurgeExpiredAuditEventsUseCase,
    record_audit_event,
)
from domain.audit.entities import AuditEvent
from domain.audit.repositories import AuditEventFilter, AuditRepository
from domain.audit.value_objects import AuditAction, AuditActorType, AuditResourceType, AuditResult


class InMemoryAuditRepository:
    def __init__(self) -> None:
        self.events: list[AuditEvent] = []

    async def create(self, event: AuditEvent) -> AuditEvent:
        self.events.append(event)
        return event

    async def search(self, filters: AuditEventFilter) -> Sequence[AuditEvent]:
        events = self.events
        if filters.start_date is not None:
            events = [event for event in events if event.timestamp >= filters.start_date]
        if filters.end_date is not None:
            events = [event for event in events if event.timestamp <= filters.end_date]
        if filters.actor_id is not None:
            events = [event for event in events if event.actor_id == filters.actor_id]
        if filters.action is not None:
            events = [event for event in events if event.action == filters.action]
        if filters.resource_type is not None:
            events = [event for event in events if event.resource_type == filters.resource_type]
        if filters.resource_id is not None:
            events = [event for event in events if event.resource_id == filters.resource_id]
        if filters.result is not None:
            events = [event for event in events if event.result is filters.result]
        ordered = sorted(events, key=lambda event: (event.timestamp, str(event.id)))
        return tuple(ordered[filters.offset : filters.offset + filters.limit])

    async def delete_older_than(self, cutoff: datetime) -> int:
        kept = [event for event in self.events if event.timestamp >= cutoff]
        deleted_count = len(self.events) - len(kept)
        self.events = kept
        return deleted_count


class InMemoryAuditUnitOfWork:
    def __init__(self) -> None:
        self.repository = InMemoryAuditRepository()
        self.committed = False

    @property
    def audits(self) -> AuditRepository:
        return self.repository

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None

    async def commit(self) -> None:
        self.committed = True

    async def rollback(self) -> None:
        return None


def test_persistent_audit_recorder_creates_success_event() -> None:
    async def run() -> None:
        unit_of_work = InMemoryAuditUnitOfWork()
        recorder = PersistentAuditRecorder(unit_of_work)

        await record_audit_event(
            recorder,
            AuditContext(
                actor_id="actor-1",
                actor_type="user",
                ip_address="127.0.0.1",
                user_agent="test-client",
                request_id="req-1",
            ),
            action="vault.create",
            resource_type="vault",
            resource_id="vault-1",
            result=AuditResult.SUCCESS,
            metadata={"name": "Production"},
        )

        assert unit_of_work.committed is True
        assert len(unit_of_work.repository.events) == 1
        assert unit_of_work.repository.events[0].action.value == "vault.create"
        assert unit_of_work.repository.events[0].result is AuditResult.SUCCESS
        assert unit_of_work.repository.events[0].metadata["protocol"] == "rest"

    anyio.run(run)


def test_audit_recorder_stores_mcp_protocol_in_metadata() -> None:
    async def run() -> None:
        unit_of_work = InMemoryAuditUnitOfWork()
        recorder = PersistentAuditRecorder(unit_of_work)

        await record_audit_event(
            recorder,
            AuditContext(actor_id="actor-1", actor_type="user", protocol="mcp"),
            action="secret.read",
            resource_type="secret",
            resource_id="secret-1",
            result=AuditResult.SUCCESS,
        )

        assert unit_of_work.repository.events[0].metadata == {"protocol": "mcp"}

    anyio.run(run)


def test_audit_query_filters_failures_and_preserves_chronological_order() -> None:
    async def run() -> None:
        unit_of_work = InMemoryAuditUnitOfWork()
        recorder = PersistentAuditRecorder(unit_of_work)
        await record_audit_event(
            recorder,
            AuditContext(actor_id="actor-1", actor_type="user"),
            "secret.decrypt",
            "secret",
            "secret-2",
            AuditResult.SUCCESS,
        )
        await record_audit_event(
            recorder,
            AuditContext(actor_id="actor-1", actor_type="user"),
            "secret.decrypt",
            "secret",
            "secret-1",
            AuditResult.FAILURE,
        )

        response = await ListAuditEventsUseCase(unit_of_work).execute(
            AuditQueryRequest(
                actor_id="actor-1",
                action="secret.decrypt",
                resource_type="secret",
                result="failure",
            )
        )

        assert len(response) == 1
        assert response[0].resource_id == "secret-1"
        assert response[0].result == "FAILURE"

    anyio.run(run)


def test_audit_retention_deletes_events_older_than_policy() -> None:
    async def run() -> None:
        unit_of_work = InMemoryAuditUnitOfWork()
        old_event = AuditEvent.create(
            actor_id=None,
            actor_type=AuditActorType("anonymous"),
            action=AuditAction("vault.create"),
            resource_type=AuditResourceType("vault"),
            resource_id="old",
            result=AuditResult.SUCCESS,
            ip_address=None,
            user_agent=None,
            request_id=None,
        )
        fresh_event = AuditEvent.create(
            actor_id=None,
            actor_type=AuditActorType("anonymous"),
            action=AuditAction("vault.create"),
            resource_type=AuditResourceType("vault"),
            resource_id="fresh",
            result=AuditResult.SUCCESS,
            ip_address=None,
            user_agent=None,
            request_id=None,
        )
        object.__setattr__(old_event, "timestamp", datetime(2026, 1, 1, tzinfo=UTC))
        object.__setattr__(fresh_event, "timestamp", datetime(2026, 7, 20, tzinfo=UTC))
        unit_of_work.repository.events.extend([old_event, fresh_event])

        deleted_count = await PurgeExpiredAuditEventsUseCase(
            unit_of_work,
            retention_days=30,
        ).execute(now=datetime(2026, 7, 21, tzinfo=UTC))

        assert deleted_count == 1
        assert unit_of_work.repository.events == [fresh_event]

    anyio.run(run)

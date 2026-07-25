from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from domain.audit.entities import AuditEvent
from domain.audit.value_objects import AuditAction, AuditEventId, AuditResourceType, AuditResult


class AuditRepositoryConflictError(RuntimeError):
    """Raised when persistence detects an AuditEvent constraint conflict."""


@dataclass(frozen=True, slots=True)
class AuditEventFilter:
    start_date: datetime | None = None
    end_date: datetime | None = None
    actor_id: str | None = None
    query: str | None = None
    action: AuditAction | None = None
    resource_type: AuditResourceType | None = None
    resource_id: str | None = None
    result: AuditResult | None = None
    limit: int = 100
    offset: int = 0


class AuditRepository(Protocol):
    async def create(self, event: AuditEvent) -> AuditEvent:
        raise NotImplementedError

    async def get(self, event_id: AuditEventId) -> AuditEvent | None:
        raise NotImplementedError

    async def search(self, filters: AuditEventFilter) -> Sequence[AuditEvent]:
        raise NotImplementedError

    async def delete_older_than(self, cutoff: datetime) -> int:
        raise NotImplementedError


class AuditRecorder(Protocol):
    async def record(self, event: AuditEvent) -> None:
        raise NotImplementedError

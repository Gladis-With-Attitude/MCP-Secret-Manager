from __future__ import annotations

from collections.abc import Mapping
from datetime import UTC, datetime, timedelta

from application.audit.dto import AuditContext, AuditEventResponse, AuditQueryRequest
from application.audit.exceptions import AuditValidationError
from application.audit.unit_of_work import AuditUnitOfWork
from domain.audit.entities import AuditEvent, JsonValue
from domain.audit.exceptions import AuditDomainError
from domain.audit.repositories import AuditEventFilter, AuditRecorder
from domain.audit.value_objects import (
    AuditAction,
    AuditActorType,
    AuditResourceType,
    AuditResult,
)


class NoopAuditRecorder:
    async def record(self, event: AuditEvent) -> None:
        _ = event
        return None


class PersistentAuditRecorder:
    def __init__(self, unit_of_work: AuditUnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def record(self, event: AuditEvent) -> None:
        async with self._unit_of_work as unit_of_work:
            await unit_of_work.audits.create(event)
            await unit_of_work.commit()


async def record_audit_event(
    recorder: AuditRecorder,
    context: AuditContext | None,
    action: str,
    resource_type: str,
    resource_id: str | None,
    result: AuditResult,
    metadata: Mapping[str, JsonValue] | None = None,
) -> None:
    resolved_context = context or AuditContext()
    try:
        event = AuditEvent.create(
            actor_id=resolved_context.actor_id,
            actor_type=AuditActorType(resolved_context.actor_type),
            action=AuditAction(action),
            resource_type=AuditResourceType(resource_type),
            resource_id=resource_id,
            result=result,
            ip_address=resolved_context.ip_address,
            user_agent=resolved_context.user_agent,
            request_id=resolved_context.request_id,
            metadata=metadata,
        )
    except AuditDomainError as exc:
        raise AuditValidationError(str(exc)) from exc
    await recorder.record(event)


class ListAuditEventsUseCase:
    def __init__(self, unit_of_work: AuditUnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def execute(self, request: AuditQueryRequest) -> tuple[AuditEventResponse, ...]:
        filters = self._validate_filters(request)
        async with self._unit_of_work as unit_of_work:
            events = await unit_of_work.audits.search(filters)
        return tuple(AuditEventResponse.from_domain(event) for event in events)

    @staticmethod
    def _validate_filters(request: AuditQueryRequest) -> AuditEventFilter:
        try:
            return AuditEventFilter(
                start_date=ListAuditEventsUseCase._parse_datetime(request.start_date),
                end_date=ListAuditEventsUseCase._parse_datetime(request.end_date),
                actor_id=ListAuditEventsUseCase._normalize_optional(request.actor_id),
                action=AuditAction(request.action) if request.action is not None else None,
                resource_type=AuditResourceType(request.resource_type)
                if request.resource_type is not None
                else None,
                resource_id=ListAuditEventsUseCase._normalize_optional(request.resource_id),
                result=AuditResult(request.result.upper()) if request.result is not None else None,
                limit=ListAuditEventsUseCase._validate_limit(request.limit),
                offset=ListAuditEventsUseCase._validate_offset(request.offset),
            )
        except (AuditDomainError, ValueError) as exc:
            raise AuditValidationError(str(exc)) from exc

    @staticmethod
    def _parse_datetime(value: str | None) -> datetime | None:
        if value is None:
            return None
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError as exc:
            raise AuditValidationError("Audit date filters must be valid datetimes.") from exc
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=UTC)
        return parsed

    @staticmethod
    def _normalize_optional(value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        if stripped == "":
            return None
        return stripped

    @staticmethod
    def _validate_limit(limit: int) -> int:
        if limit < 1 or limit > 500:
            raise AuditValidationError("Audit query limit must be between 1 and 500.")
        return limit

    @staticmethod
    def _validate_offset(offset: int) -> int:
        if offset < 0:
            raise AuditValidationError("Audit query offset must be greater than or equal to 0.")
        return offset


class PurgeExpiredAuditEventsUseCase:
    def __init__(self, unit_of_work: AuditUnitOfWork, retention_days: int) -> None:
        if retention_days < 1:
            raise AuditValidationError("Audit retention must be at least 1 day.")
        self._unit_of_work = unit_of_work
        self._retention_days = retention_days

    async def execute(self, now: datetime | None = None) -> int:
        resolved_now = now or datetime.now(UTC)
        cutoff = resolved_now - timedelta(days=self._retention_days)
        async with self._unit_of_work as unit_of_work:
            deleted_count = await unit_of_work.audits.delete_older_than(cutoff)
            await unit_of_work.commit()
        return deleted_count

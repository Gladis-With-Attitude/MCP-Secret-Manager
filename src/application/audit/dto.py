from __future__ import annotations

from dataclasses import dataclass

from domain.audit.entities import AuditEvent, AuditMetadata


@dataclass(frozen=True, slots=True)
class AuditContext:
    actor_id: str | None = None
    actor_type: str = "anonymous"
    ip_address: str | None = None
    user_agent: str | None = None
    request_id: str | None = None


@dataclass(frozen=True, slots=True)
class AuditQueryRequest:
    start_date: str | None = None
    end_date: str | None = None
    actor_id: str | None = None
    action: str | None = None
    resource_type: str | None = None
    resource_id: str | None = None
    result: str | None = None
    limit: int = 100
    offset: int = 0


@dataclass(frozen=True, slots=True)
class AuditEventResponse:
    id: str
    timestamp: str
    actor_id: str | None
    actor_type: str
    action: str
    resource_type: str
    resource_id: str | None
    result: str
    ip_address: str | None
    user_agent: str | None
    request_id: str | None
    metadata: AuditMetadata

    @classmethod
    def from_domain(cls, event: AuditEvent) -> AuditEventResponse:
        return cls(
            id=str(event.id),
            timestamp=event.timestamp.isoformat(),
            actor_id=event.actor_id,
            actor_type=event.actor_type.value,
            action=event.action.value,
            resource_type=event.resource_type.value,
            resource_id=event.resource_id,
            result=event.result.value,
            ip_address=event.ip_address,
            user_agent=event.user_agent,
            request_id=event.request_id,
            metadata=event.metadata,
        )

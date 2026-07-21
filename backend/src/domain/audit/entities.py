from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime

from domain.audit.value_objects import (
    AuditAction,
    AuditActorType,
    AuditEventId,
    AuditResourceType,
    AuditResult,
)

type JsonValue = str | int | float | bool | None | Mapping[str, JsonValue] | Sequence[JsonValue]
type AuditMetadata = Mapping[str, JsonValue]


@dataclass(frozen=True, slots=True, eq=False)
class AuditEvent:
    id: AuditEventId
    timestamp: datetime
    actor_id: str | None
    actor_type: AuditActorType
    action: AuditAction
    resource_type: AuditResourceType
    resource_id: str | None
    result: AuditResult
    ip_address: str | None
    user_agent: str | None
    request_id: str | None
    metadata: AuditMetadata

    @classmethod
    def create(
        cls,
        actor_id: str | None,
        actor_type: AuditActorType,
        action: AuditAction,
        resource_type: AuditResourceType,
        resource_id: str | None,
        result: AuditResult,
        ip_address: str | None,
        user_agent: str | None,
        request_id: str | None,
        metadata: AuditMetadata | None = None,
    ) -> AuditEvent:
        return cls(
            id=AuditEventId.new(),
            timestamp=datetime.now(UTC),
            actor_id=cls._normalize_optional(actor_id),
            actor_type=actor_type,
            action=action,
            resource_type=resource_type,
            resource_id=cls._normalize_optional(resource_id),
            result=result,
            ip_address=cls._normalize_optional(ip_address),
            user_agent=cls._normalize_optional(user_agent),
            request_id=cls._normalize_optional(request_id),
            metadata=dict(metadata or {}),
        )

    @staticmethod
    def _normalize_optional(value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        if stripped == "":
            return None
        return stripped

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AuditEvent):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

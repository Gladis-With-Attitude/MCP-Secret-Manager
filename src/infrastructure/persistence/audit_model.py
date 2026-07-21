from __future__ import annotations

from collections.abc import Mapping
from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, Index, String, Text
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column

from domain.audit.entities import AuditEvent, JsonValue
from domain.audit.value_objects import (
    AuditAction,
    AuditActorType,
    AuditEventId,
    AuditResourceType,
    AuditResult,
)
from infrastructure.persistence.base import Base


class AuditEventModel(Base):
    __tablename__ = "audit_events"
    __table_args__ = (
        CheckConstraint("result IN ('SUCCESS', 'FAILURE')", name="ck_audit_events_result"),
        Index("ix_audit_events_timestamp", "timestamp"),
        Index("ix_audit_events_actor_id", "actor_id"),
        Index("ix_audit_events_resource_type", "resource_type"),
        Index("ix_audit_events_action", "action"),
        Index("ix_audit_events_result", "result"),
    )

    id: Mapped[UUID] = mapped_column(postgresql.UUID(as_uuid=True), primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    actor_id: Mapped[str | None] = mapped_column(String(length=128), nullable=True)
    actor_type: Mapped[str] = mapped_column(String(length=32), nullable=False)
    action: Mapped[str] = mapped_column(String(length=120), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(length=64), nullable=False)
    resource_id: Mapped[str | None] = mapped_column(String(length=128), nullable=True)
    result: Mapped[str] = mapped_column(String(length=16), nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(length=64), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    request_id: Mapped[str | None] = mapped_column(String(length=128), nullable=True)
    metadata_json: Mapped[Mapping[str, JsonValue]] = mapped_column(
        "metadata",
        postgresql.JSONB,
        nullable=False,
    )

    @classmethod
    def from_domain(cls, event: AuditEvent) -> AuditEventModel:
        return cls(
            id=event.id.value,
            timestamp=event.timestamp,
            actor_id=event.actor_id,
            actor_type=event.actor_type.value,
            action=event.action.value,
            resource_type=event.resource_type.value,
            resource_id=event.resource_id,
            result=event.result.value,
            ip_address=event.ip_address,
            user_agent=event.user_agent,
            request_id=event.request_id,
            metadata_json=event.metadata,
        )

    def to_domain(self) -> AuditEvent:
        return AuditEvent(
            id=AuditEventId(self.id),
            timestamp=self.timestamp,
            actor_id=self.actor_id,
            actor_type=AuditActorType(self.actor_type),
            action=AuditAction(self.action),
            resource_type=AuditResourceType(self.resource_type),
            resource_id=self.resource_id,
            result=AuditResult(self.result),
            ip_address=self.ip_address,
            user_agent=self.user_agent,
            request_id=self.request_id,
            metadata=self.metadata_json,
        )

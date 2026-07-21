from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from domain.audit.entities import AuditEvent
from domain.audit.repositories import AuditEventFilter, AuditRepositoryConflictError
from infrastructure.persistence.audit_model import AuditEventModel


class SqlAlchemyAuditRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, event: AuditEvent) -> AuditEvent:
        model = AuditEventModel.from_domain(event)
        self._session.add(model)
        try:
            await self._session.flush()
        except IntegrityError as exc:
            raise AuditRepositoryConflictError("AuditEvent persistence conflict.") from exc
        return model.to_domain()

    async def search(self, filters: AuditEventFilter) -> Sequence[AuditEvent]:
        statement = select(AuditEventModel)
        if filters.start_date is not None:
            statement = statement.where(AuditEventModel.timestamp >= filters.start_date)
        if filters.end_date is not None:
            statement = statement.where(AuditEventModel.timestamp <= filters.end_date)
        if filters.actor_id is not None:
            statement = statement.where(AuditEventModel.actor_id == filters.actor_id)
        if filters.action is not None:
            statement = statement.where(AuditEventModel.action == filters.action.value)
        if filters.resource_type is not None:
            statement = statement.where(
                AuditEventModel.resource_type == filters.resource_type.value
            )
        if filters.resource_id is not None:
            statement = statement.where(AuditEventModel.resource_id == filters.resource_id)
        if filters.result is not None:
            statement = statement.where(AuditEventModel.result == filters.result.value)

        statement = (
            statement.order_by(AuditEventModel.timestamp.asc(), AuditEventModel.id.asc())
            .limit(filters.limit)
            .offset(filters.offset)
        )
        result = await self._session.scalars(statement)
        return tuple(model.to_domain() for model in result.all())

    async def delete_older_than(self, cutoff: datetime) -> int:
        result = await self._session.scalars(
            delete(AuditEventModel)
            .where(AuditEventModel.timestamp < cutoff)
            .returning(AuditEventModel.id)
        )
        return len(result.all())

from __future__ import annotations

from types import TracebackType
from typing import Protocol

from domain.audit.repositories import AuditRepository


class AuditUnitOfWork(Protocol):
    @property
    def audits(self) -> AuditRepository:
        raise NotImplementedError

    async def __aenter__(self) -> AuditUnitOfWork:
        raise NotImplementedError

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        raise NotImplementedError

    async def commit(self) -> None:
        raise NotImplementedError

    async def rollback(self) -> None:
        raise NotImplementedError

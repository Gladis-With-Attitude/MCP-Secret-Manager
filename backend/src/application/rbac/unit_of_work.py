from __future__ import annotations

from types import TracebackType
from typing import Protocol

from domain.rbac.repositories import PermissionRepository, RoleAssignmentRepository, RoleRepository


class RbacUnitOfWork(Protocol):
    @property
    def permissions(self) -> PermissionRepository:
        raise NotImplementedError

    @property
    def roles(self) -> RoleRepository:
        raise NotImplementedError

    @property
    def role_assignments(self) -> RoleAssignmentRepository:
        raise NotImplementedError

    async def __aenter__(self) -> RbacUnitOfWork:
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

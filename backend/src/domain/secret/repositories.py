from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from domain.project.value_objects import ProjectId
from domain.secret.entities import Secret
from domain.secret.value_objects import SecretId, SecretKey


class SecretRepositoryConflictError(RuntimeError):
    """Raised when persistence detects a Secret uniqueness conflict."""


class SecretRepository(Protocol):
    async def create(self, secret: Secret) -> Secret:
        raise NotImplementedError

    async def get(self, secret_id: SecretId) -> Secret | None:
        raise NotImplementedError

    async def update(self, secret: Secret) -> Secret:
        raise NotImplementedError

    async def list_by_project(
        self,
        project_id: ProjectId,
        *,
        include_archived: bool = False,
        limit: int = 20,
        offset: int = 0,
        search: str | None = None,
        status: str | None = None,
        secret_type: str | None = None,
    ) -> Sequence[Secret]:
        raise NotImplementedError

    async def count_by_project(
        self,
        project_id: ProjectId,
        *,
        include_archived: bool = False,
        search: str | None = None,
        status: str | None = None,
        secret_type: str | None = None,
    ) -> int:
        raise NotImplementedError

    async def exists_in_project(
        self,
        project_id: ProjectId,
        key: SecretKey,
        *,
        exclude_secret_id: SecretId | None = None,
    ) -> bool:
        raise NotImplementedError

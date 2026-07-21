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

    async def list_by_project(self, project_id: ProjectId) -> Sequence[Secret]:
        raise NotImplementedError

    async def exists_in_project(self, project_id: ProjectId, key: SecretKey) -> bool:
        raise NotImplementedError

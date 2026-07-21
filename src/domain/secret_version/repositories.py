from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from domain.secret.value_objects import SecretId
from domain.secret_version.entities import SecretVersion
from domain.secret_version.value_objects import SecretVersionId


class SecretVersionRepositoryConflictError(RuntimeError):
    """Raised when persistence detects a SecretVersion constraint conflict."""


class SecretVersionRepository(Protocol):
    async def create(self, secret_version: SecretVersion) -> SecretVersion:
        raise NotImplementedError

    async def get(self, secret_version_id: SecretVersionId) -> SecretVersion | None:
        raise NotImplementedError

    async def list_versions(self, secret_id: SecretId) -> Sequence[SecretVersion]:
        raise NotImplementedError

    async def get_active(self, secret_id: SecretId) -> SecretVersion | None:
        raise NotImplementedError

    async def deactivate_previous_versions(self, secret_id: SecretId) -> None:
        raise NotImplementedError

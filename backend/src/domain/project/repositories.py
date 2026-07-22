from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from domain.project.entities import Project
from domain.project.value_objects import ProjectId, ProjectName
from domain.vault.value_objects import VaultId


class ProjectRepositoryConflictError(RuntimeError):
    """Raised when persistence detects a Project uniqueness conflict."""


class ProjectRepository(Protocol):
    async def create(self, project: Project) -> Project:
        raise NotImplementedError

    async def get(self, project_id: ProjectId) -> Project | None:
        raise NotImplementedError

    async def update(self, project: Project) -> Project:
        raise NotImplementedError

    async def list_by_vault(
        self,
        vault_id: VaultId,
        *,
        include_archived: bool = False,
        limit: int = 20,
        offset: int = 0,
        search: str | None = None,
        status: str | None = None,
    ) -> Sequence[Project]:
        raise NotImplementedError

    async def count_by_vault(
        self,
        vault_id: VaultId,
        *,
        include_archived: bool = False,
        search: str | None = None,
        status: str | None = None,
    ) -> int:
        raise NotImplementedError

    async def exists_in_vault(
        self,
        vault_id: VaultId,
        name: ProjectName,
        *,
        exclude_project_id: ProjectId | None = None,
    ) -> bool:
        raise NotImplementedError

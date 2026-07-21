from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from domain.project.entities import Project
from domain.project.repositories import ProjectRepositoryConflictError
from domain.project.value_objects import ProjectId, ProjectName
from domain.vault.value_objects import VaultId
from infrastructure.persistence.project_model import ProjectModel


class SqlAlchemyProjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, project: Project) -> Project:
        model = ProjectModel.from_domain(project)
        self._session.add(model)

        try:
            await self._session.flush()
        except IntegrityError as exc:
            raise ProjectRepositoryConflictError("Project persistence conflict.") from exc

        return model.to_domain()

    async def get(self, project_id: ProjectId) -> Project | None:
        model = await self._session.get(ProjectModel, project_id.value)
        if model is None:
            return None
        return model.to_domain()

    async def list_by_vault(self, vault_id: VaultId) -> Sequence[Project]:
        result = await self._session.scalars(
            select(ProjectModel)
            .where(ProjectModel.vault_id == vault_id.value)
            .order_by(ProjectModel.name)
        )
        return tuple(model.to_domain() for model in result.all())

    async def exists_in_vault(self, vault_id: VaultId, name: ProjectName) -> bool:
        statement = (
            select(ProjectModel.id)
            .where(ProjectModel.vault_id == vault_id.value, ProjectModel.name == name.value)
            .limit(1)
        )
        result = await self._session.scalar(statement)
        return result is not None

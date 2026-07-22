from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import Select, func, or_, select
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

    async def update(self, project: Project) -> Project:
        model = await self._session.get(ProjectModel, project.id.value)
        if model is None:
            return project

        model.name = project.name.value
        model.description = project.description.value
        model.archived = project.archived
        model.created_at = project.created_at
        model.updated_at = project.updated_at
        model.archived_at = project.archived_at

        try:
            await self._session.flush()
        except IntegrityError as exc:
            raise ProjectRepositoryConflictError("Project persistence conflict.") from exc

        return model.to_domain()

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
        statement = self._filter_statement(
            select(ProjectModel).where(ProjectModel.vault_id == vault_id.value),
            include_archived=include_archived,
            search=search,
            status=status,
        )
        statement = statement.order_by(ProjectModel.name).offset(offset).limit(limit)
        result = await self._session.scalars(statement)
        return tuple(model.to_domain() for model in result.all())

    async def count_by_vault(
        self,
        vault_id: VaultId,
        *,
        include_archived: bool = False,
        search: str | None = None,
        status: str | None = None,
    ) -> int:
        statement = self._filter_statement(
            select(func.count())
            .select_from(ProjectModel)
            .where(ProjectModel.vault_id == vault_id.value),
            include_archived=include_archived,
            search=search,
            status=status,
        )
        return int(await self._session.scalar(statement) or 0)

    async def exists_in_vault(
        self,
        vault_id: VaultId,
        name: ProjectName,
        *,
        exclude_project_id: ProjectId | None = None,
    ) -> bool:
        statement = (
            select(ProjectModel.id)
            .where(ProjectModel.vault_id == vault_id.value, ProjectModel.name == name.value)
            .limit(1)
        )
        if exclude_project_id is not None:
            statement = statement.where(ProjectModel.id != exclude_project_id.value)
        result = await self._session.scalar(statement)
        return result is not None

    @staticmethod
    def _filter_statement(
        statement: Select[tuple[ProjectModel]] | Select[tuple[int]],
        *,
        include_archived: bool,
        search: str | None,
        status: str | None,
    ) -> Select[tuple[ProjectModel]] | Select[tuple[int]]:
        normalized_status = status.strip().lower() if status else None

        if normalized_status == "archived":
            statement = statement.where(ProjectModel.archived.is_(True))
        elif normalized_status == "active" or not include_archived:
            statement = statement.where(ProjectModel.archived.is_(False))

        normalized_search = search.strip() if search else None
        if normalized_search:
            pattern = f"%{normalized_search}%"
            statement = statement.where(
                or_(
                    ProjectModel.name.ilike(pattern),
                    ProjectModel.description.ilike(pattern),
                )
            )

        return statement

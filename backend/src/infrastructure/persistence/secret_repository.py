from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import Select, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from domain.project.value_objects import ProjectId
from domain.secret.entities import Secret
from domain.secret.repositories import SecretRepositoryConflictError
from domain.secret.value_objects import SecretId, SecretKey
from infrastructure.persistence.secret_model import SecretModel


class SqlAlchemySecretRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, secret: Secret) -> Secret:
        model = SecretModel.from_domain(secret)
        self._session.add(model)

        try:
            await self._session.flush()
        except IntegrityError as exc:
            raise SecretRepositoryConflictError("Secret persistence conflict.") from exc

        return model.to_domain()

    async def get(self, secret_id: SecretId) -> Secret | None:
        model = await self._session.get(SecretModel, secret_id.value)
        if model is None:
            return None
        return model.to_domain()

    async def update(self, secret: Secret) -> Secret:
        model = await self._session.get(SecretModel, secret.id.value)
        if model is None:
            return secret

        model.key = secret.key.value
        model.description = secret.description.value
        model.type = secret.type.value
        model.metadata_json = secret.metadata.value
        model.tags = list(secret.tags.value)
        model.archived = secret.archived
        model.created_at = secret.created_at
        model.updated_at = secret.updated_at
        model.archived_at = secret.archived_at

        try:
            await self._session.flush()
        except IntegrityError as exc:
            raise SecretRepositoryConflictError("Secret persistence conflict.") from exc

        return model.to_domain()

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
        statement = self._filter_statement(
            select(SecretModel).where(SecretModel.project_id == project_id.value),
            include_archived=include_archived,
            search=search,
            status=status,
            secret_type=secret_type,
        )
        statement = statement.order_by(SecretModel.key).offset(offset).limit(limit)
        result = await self._session.scalars(statement)
        return tuple(model.to_domain() for model in result.all())

    async def count_by_project(
        self,
        project_id: ProjectId,
        *,
        include_archived: bool = False,
        search: str | None = None,
        status: str | None = None,
        secret_type: str | None = None,
    ) -> int:
        statement = self._filter_statement(
            select(func.count())
            .select_from(SecretModel)
            .where(SecretModel.project_id == project_id.value),
            include_archived=include_archived,
            search=search,
            status=status,
            secret_type=secret_type,
        )
        return int(await self._session.scalar(statement) or 0)

    async def exists_in_project(
        self,
        project_id: ProjectId,
        key: SecretKey,
        *,
        exclude_secret_id: SecretId | None = None,
    ) -> bool:
        statement = (
            select(SecretModel.id)
            .where(SecretModel.project_id == project_id.value, SecretModel.key == key.value)
            .limit(1)
        )
        if exclude_secret_id is not None:
            statement = statement.where(SecretModel.id != exclude_secret_id.value)
        result = await self._session.scalar(statement)
        return result is not None

    @staticmethod
    def _filter_statement(
        statement: Select[tuple[SecretModel]] | Select[tuple[int]],
        *,
        include_archived: bool,
        search: str | None,
        status: str | None,
        secret_type: str | None,
    ) -> Select[tuple[SecretModel]] | Select[tuple[int]]:
        normalized_status = status.strip().lower() if status else None

        if normalized_status == "archived":
            statement = statement.where(SecretModel.archived.is_(True))
        elif normalized_status == "active" or not include_archived:
            statement = statement.where(SecretModel.archived.is_(False))

        normalized_type = secret_type.strip().lower() if secret_type else None
        if normalized_type:
            statement = statement.where(SecretModel.type == normalized_type)

        normalized_search = search.strip() if search else None
        if normalized_search:
            pattern = f"%{normalized_search}%"
            statement = statement.where(
                or_(
                    SecretModel.key.ilike(pattern),
                    SecretModel.description.ilike(pattern),
                )
            )

        return statement

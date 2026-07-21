from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
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

    async def list_by_project(self, project_id: ProjectId) -> Sequence[Secret]:
        result = await self._session.scalars(
            select(SecretModel)
            .where(SecretModel.project_id == project_id.value)
            .order_by(SecretModel.key)
        )
        return tuple(model.to_domain() for model in result.all())

    async def exists_in_project(self, project_id: ProjectId, key: SecretKey) -> bool:
        statement = (
            select(SecretModel.id)
            .where(SecretModel.project_id == project_id.value, SecretModel.key == key.value)
            .limit(1)
        )
        result = await self._session.scalar(statement)
        return result is not None

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from domain.secret.value_objects import SecretId
from domain.secret_version.entities import SecretVersion
from domain.secret_version.repositories import SecretVersionRepositoryConflictError
from domain.secret_version.value_objects import SecretVersionId
from infrastructure.persistence.secret_version_model import SecretVersionModel


class SqlAlchemySecretVersionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, secret_version: SecretVersion) -> SecretVersion:
        model = SecretVersionModel.from_domain(secret_version)
        self._session.add(model)

        try:
            await self._session.flush()
        except IntegrityError as exc:
            raise SecretVersionRepositoryConflictError(
                "SecretVersion persistence conflict."
            ) from exc

        return model.to_domain()

    async def get(self, secret_version_id: SecretVersionId) -> SecretVersion | None:
        model = await self._session.get(SecretVersionModel, secret_version_id.value)
        if model is None:
            return None
        return model.to_domain()

    async def list_versions(self, secret_id: SecretId) -> Sequence[SecretVersion]:
        result = await self._session.scalars(
            select(SecretVersionModel)
            .where(SecretVersionModel.secret_id == secret_id.value)
            .order_by(SecretVersionModel.version)
        )
        return tuple(model.to_domain() for model in result.all())

    async def get_active(self, secret_id: SecretId) -> SecretVersion | None:
        result = await self._session.scalar(
            select(SecretVersionModel).where(
                SecretVersionModel.secret_id == secret_id.value,
                SecretVersionModel.active.is_(True),
            )
        )
        if result is None:
            return None
        return result.to_domain()

    async def deactivate_previous_versions(self, secret_id: SecretId) -> None:
        await self._session.execute(
            update(SecretVersionModel)
            .where(
                SecretVersionModel.secret_id == secret_id.value,
                SecretVersionModel.active.is_(True),
            )
            .values(active=False)
        )

    async def activate(self, secret_version_id: SecretVersionId) -> SecretVersion:
        model = await self._session.get(SecretVersionModel, secret_version_id.value)
        if model is None:
            raise SecretVersionRepositoryConflictError("SecretVersion not found.")
        model.active = True
        try:
            await self._session.flush()
        except IntegrityError as exc:
            raise SecretVersionRepositoryConflictError(
                "SecretVersion persistence conflict."
            ) from exc
        return model.to_domain()

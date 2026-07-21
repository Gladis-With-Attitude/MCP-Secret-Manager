from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from domain.identity.entities import ApiKey, ServiceAccount, User
from domain.identity.repositories import (
    ApiKeyRepositoryConflictError,
    ServiceAccountRepositoryConflictError,
    UserRepositoryConflictError,
)
from domain.identity.value_objects import (
    ApiKeyId,
    ServiceAccountId,
    ServiceAccountName,
    UserEmail,
    UserId,
)
from domain.project.value_objects import ProjectId
from infrastructure.persistence.identity_models import (
    ApiKeyModel,
    ServiceAccountModel,
    UserModel,
)


class SqlAlchemyUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, user: User) -> User:
        model = UserModel.from_domain(user)
        self._session.add(model)
        try:
            await self._session.flush()
        except IntegrityError as exc:
            raise UserRepositoryConflictError("User persistence conflict.") from exc
        return model.to_domain()

    async def get(self, user_id: UserId) -> User | None:
        model = await self._session.get(UserModel, user_id.value)
        if model is None:
            return None
        return model.to_domain()

    async def get_by_email(self, email: UserEmail) -> User | None:
        model = await self._session.scalar(select(UserModel).where(UserModel.email == email.value))
        if model is None:
            return None
        return model.to_domain()


class SqlAlchemyServiceAccountRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, service_account: ServiceAccount) -> ServiceAccount:
        model = ServiceAccountModel.from_domain(service_account)
        self._session.add(model)
        try:
            await self._session.flush()
        except IntegrityError as exc:
            raise ServiceAccountRepositoryConflictError(
                "ServiceAccount persistence conflict."
            ) from exc
        return model.to_domain()

    async def get(self, service_account_id: ServiceAccountId) -> ServiceAccount | None:
        model = await self._session.get(ServiceAccountModel, service_account_id.value)
        if model is None:
            return None
        return model.to_domain()

    async def exists_in_project(self, project_id: ProjectId, name: ServiceAccountName) -> bool:
        result = await self._session.scalar(
            select(ServiceAccountModel.id)
            .where(
                ServiceAccountModel.project_id == project_id.value,
                ServiceAccountModel.name == name.value,
            )
            .limit(1)
        )
        return result is not None


class SqlAlchemyApiKeyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, api_key: ApiKey) -> ApiKey:
        model = ApiKeyModel.from_domain(api_key)
        self._session.add(model)
        try:
            await self._session.flush()
        except IntegrityError as exc:
            raise ApiKeyRepositoryConflictError("ApiKey persistence conflict.") from exc
        return model.to_domain()

    async def get(self, api_key_id: ApiKeyId) -> ApiKey | None:
        model = await self._session.get(ApiKeyModel, api_key_id.value)
        if model is None:
            return None
        return model.to_domain()

    async def get_by_prefix(self, key_prefix: str) -> ApiKey | None:
        model = await self._session.scalar(
            select(ApiKeyModel).where(ApiKeyModel.key_prefix == key_prefix)
        )
        if model is None:
            return None
        return model.to_domain()

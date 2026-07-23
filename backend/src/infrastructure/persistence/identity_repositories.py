from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from domain.identity.entities import ApiKey, AuthSession, ServiceAccount, User
from domain.identity.repositories import (
    ApiKeyRepositoryConflictError,
    AuthSessionRepositoryConflictError,
    ServiceAccountRepositoryConflictError,
    UserRepositoryConflictError,
)
from domain.identity.value_objects import (
    ApiKeyId,
    ServiceAccountId,
    ServiceAccountName,
    SessionId,
    UserEmail,
    UserId,
)
from domain.project.value_objects import ProjectId
from infrastructure.persistence.identity_models import (
    ApiKeyModel,
    AuthSessionModel,
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


class SqlAlchemyAuthSessionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, auth_session: AuthSession) -> AuthSession:
        model = AuthSessionModel.from_domain(auth_session)
        self._session.add(model)
        try:
            await self._session.flush()
        except IntegrityError as exc:
            raise AuthSessionRepositoryConflictError("AuthSession persistence conflict.") from exc
        return model.to_domain()

    async def get(self, session_id: SessionId) -> AuthSession | None:
        model = await self._session.get(AuthSessionModel, session_id.value)
        if model is None:
            return None
        return model.to_domain()

    async def get_by_prefix(self, token_prefix: str) -> AuthSession | None:
        model = await self._session.scalar(
            select(AuthSessionModel).where(AuthSessionModel.token_prefix == token_prefix)
        )
        if model is None:
            return None
        return model.to_domain()

    async def update(self, auth_session: AuthSession) -> AuthSession:
        model = await self._session.get(AuthSessionModel, auth_session.id.value)
        if model is None:
            raise AuthSessionRepositoryConflictError("AuthSession was not found.")
        model.hashed_token = auth_session.hashed_token
        model.token_prefix = auth_session.token_prefix
        model.api_key_id = auth_session.api_key_id.value
        model.owner_id = auth_session.owner_id.value
        model.owner_type = auth_session.owner_type.value
        model.expires_at = auth_session.expires_at
        model.revoked_at = auth_session.revoked_at
        model.created_at = auth_session.created_at
        model.last_seen_at = auth_session.last_seen_at
        try:
            await self._session.flush()
        except IntegrityError as exc:
            raise AuthSessionRepositoryConflictError("AuthSession persistence conflict.") from exc
        return model.to_domain()

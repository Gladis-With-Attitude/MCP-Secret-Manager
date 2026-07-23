from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import ColumnElement

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

    async def list(
        self,
        *,
        limit: int = 20,
        offset: int = 0,
        search: str | None = None,
        status: str | None = None,
        now: datetime | None = None,
    ) -> tuple[ApiKey, ...]:
        statement = (
            select(ApiKeyModel)
            .where(*self._filters(search=search, status=status, now=now))
            .order_by(ApiKeyModel.created_at.desc(), ApiKeyModel.id.desc())
            .limit(limit)
            .offset(offset)
        )
        models = await self._session.scalars(statement)
        return tuple(model.to_domain() for model in models)

    async def count(
        self,
        *,
        search: str | None = None,
        status: str | None = None,
        now: datetime | None = None,
    ) -> int:
        statement = (
            select(func.count())
            .select_from(ApiKeyModel)
            .where(*self._filters(search=search, status=status, now=now))
        )
        return int(await self._session.scalar(statement) or 0)

    async def update(self, api_key: ApiKey) -> ApiKey:
        model = await self._session.get(ApiKeyModel, api_key.id.value)
        if model is None:
            raise ApiKeyRepositoryConflictError("ApiKey was not found.")
        model.hashed_key = api_key.hashed_key
        model.key_prefix = api_key.key_prefix
        model.owner_id = api_key.owner_id.value
        model.owner_type = api_key.owner_type.value
        model.name = api_key.name
        model.description = api_key.description
        model.granted_permissions = list(api_key.granted_permissions)
        model.scopes = list(api_key.scopes)
        model.expires_at = api_key.expires_at
        model.revoked_at = api_key.revoked_at
        model.created_at = api_key.created_at
        try:
            await self._session.flush()
        except IntegrityError as exc:
            raise ApiKeyRepositoryConflictError("ApiKey persistence conflict.") from exc
        return model.to_domain()

    @staticmethod
    def _filters(
        *,
        search: str | None,
        status: str | None,
        now: datetime | None,
    ) -> tuple[ColumnElement[bool], ...]:
        filters: list[ColumnElement[bool]] = []
        if search:
            search_pattern = f"%{search.lower()}%"
            filters.append(
                or_(
                    func.lower(ApiKeyModel.key_prefix).like(search_pattern),
                    func.lower(ApiKeyModel.name).like(search_pattern),
                    func.lower(ApiKeyModel.owner_type).like(search_pattern),
                )
            )

        if status:
            effective_now = now or datetime.now(UTC)
            if status == "active":
                filters.append(ApiKeyModel.revoked_at.is_(None))
                filters.append(
                    or_(ApiKeyModel.expires_at.is_(None), ApiKeyModel.expires_at > effective_now)
                )
            elif status == "expired":
                filters.append(ApiKeyModel.revoked_at.is_(None))
                filters.append(ApiKeyModel.expires_at.is_not(None))
                filters.append(ApiKeyModel.expires_at <= effective_now)
            elif status == "revoked":
                filters.append(ApiKeyModel.revoked_at.is_not(None))
            elif status == "unknown":
                filters.append(ApiKeyModel.id.is_(None))

        return tuple(filters)


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

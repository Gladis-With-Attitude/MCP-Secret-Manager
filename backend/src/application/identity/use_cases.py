from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import ClassVar

from application.audit.dto import AuditContext
from application.audit.use_cases import NoopAuditRecorder, record_audit_event
from application.identity.dto import (
    ApiKeyCreatedResponse,
    ApiKeyListResponse,
    ApiKeyPaginationResponse,
    ApiKeyPermissionsResponse,
    ApiKeyResponse,
    AuthenticatedIdentityResponse,
    CreateApiKeyRequest,
    CreateServiceAccountRequest,
    CreateSessionRequest,
    CreateUserRequest,
    CurrentSessionResponse,
    GetApiKeyRequest,
    ListApiKeysRequest,
    RevokeApiKeyRequest,
    ServiceAccountResponse,
    SessionCreatedResponse,
    UpdateApiKeyRequest,
    UserResponse,
)
from application.identity.exceptions import (
    AuthenticationFailedError,
    IdentityConflictError,
    IdentityNotFoundError,
    IdentityValidationError,
)
from application.identity.unit_of_work import IdentityUnitOfWork
from application.observability import log_application_event
from domain.audit.repositories import AuditRecorder
from domain.audit.value_objects import AuditResult
from domain.identity.entities import ApiKey, AuthSession, ServiceAccount, User
from domain.identity.exceptions import IdentityDomainError
from domain.identity.repositories import (
    ApiKeyRepositoryConflictError,
    ServiceAccountRepositoryConflictError,
    UserRepositoryConflictError,
)
from domain.identity.services import ApiKeyHasher, ApiKeySecretGenerator, SessionTokenGenerator
from domain.identity.value_objects import (
    ApiKeyId,
    ApiKeyOwnerType,
    IdentityStatus,
    ServiceAccountId,
    ServiceAccountName,
    SessionId,
    UserDisplayName,
    UserEmail,
    UserId,
)
from domain.project.value_objects import ProjectId

logger = logging.getLogger(__name__)


class CreateUserUseCase:
    def __init__(self, unit_of_work: IdentityUnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def execute(self, request: CreateUserRequest) -> UserResponse:
        email = self._validate_email(request.email)
        display_name = self._validate_display_name(request.display_name)

        async with self._unit_of_work as unit_of_work:
            user = User.create(email=email, display_name=display_name)
            try:
                created = await unit_of_work.users.create(user)
            except UserRepositoryConflictError as exc:
                raise IdentityConflictError("A user with this email already exists.") from exc
            await unit_of_work.commit()

        return UserResponse.from_domain(created)

    @staticmethod
    def _validate_email(raw_email: str) -> UserEmail:
        try:
            return UserEmail(raw_email)
        except IdentityDomainError as exc:
            raise IdentityValidationError(str(exc)) from exc

    @staticmethod
    def _validate_display_name(raw_display_name: str) -> UserDisplayName:
        try:
            return UserDisplayName(raw_display_name)
        except IdentityDomainError as exc:
            raise IdentityValidationError(str(exc)) from exc


class CreateServiceAccountUseCase:
    def __init__(self, unit_of_work: IdentityUnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def execute(self, request: CreateServiceAccountRequest) -> ServiceAccountResponse:
        project_id = self._validate_project_id(request.project_id)
        name = self._validate_name(request.name)
        description = request.description.strip() if request.description is not None else None
        if description == "":
            description = None

        async with self._unit_of_work as unit_of_work:
            project = await unit_of_work.projects.get(project_id)
            if project is None:
                raise IdentityNotFoundError("Project not found.")

            service_account = ServiceAccount.create(
                project_id=project_id,
                name=name,
                description=description,
            )
            try:
                created = await unit_of_work.service_accounts.create(service_account)
            except ServiceAccountRepositoryConflictError as exc:
                raise IdentityConflictError(
                    "A service account with this name already exists in this project."
                ) from exc
            await unit_of_work.commit()

        return ServiceAccountResponse.from_domain(created)

    @staticmethod
    def _validate_project_id(raw_project_id: str) -> ProjectId:
        try:
            return ProjectId.from_string(raw_project_id)
        except ValueError as exc:
            raise IdentityValidationError("Project id must be a valid UUID.") from exc

    @staticmethod
    def _validate_name(raw_name: str) -> ServiceAccountName:
        try:
            return ServiceAccountName(raw_name)
        except IdentityDomainError as exc:
            raise IdentityValidationError(str(exc)) from exc


class CreateApiKeyUseCase:
    def __init__(
        self,
        unit_of_work: IdentityUnitOfWork,
        api_key_generator: ApiKeySecretGenerator,
        api_key_hasher: ApiKeyHasher,
        audit_recorder: AuditRecorder | None = None,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._api_key_generator = api_key_generator
        self._api_key_hasher = api_key_hasher
        self._audit_recorder = audit_recorder or NoopAuditRecorder()

    async def execute(self, request: CreateApiKeyRequest) -> ApiKeyCreatedResponse:
        try:
            owner_type = self._validate_owner_type(request.owner_type)
            owner_id = self._validate_owner_id(request.owner_id, owner_type)
            expires_at = self._validate_expires_at(request.expires_at)
            name = self._validate_name(request.name)
            description = self._validate_description(request.description)
            granted_permissions = self._validate_string_tuple(
                request.granted_permissions,
                field_name="API key permissions",
            )
            scopes = self._validate_string_tuple(request.scopes, field_name="API key scopes")
            raw_api_key = self._api_key_generator.generate()
            key_prefix = self._api_key_generator.extract_prefix(raw_api_key)
            if key_prefix is None:
                raise IdentityValidationError("Generated API key prefix is invalid.")
            hashed_key = self._api_key_hasher.hash(raw_api_key)

            async with self._unit_of_work as unit_of_work:
                await self._ensure_active_owner(unit_of_work, owner_id, owner_type)
                api_key = ApiKey.create(
                    hashed_key=hashed_key,
                    key_prefix=key_prefix,
                    owner_id=owner_id,
                    owner_type=owner_type,
                    expires_at=expires_at,
                    name=name,
                    description=description,
                    granted_permissions=granted_permissions,
                    scopes=scopes,
                )
                try:
                    created = await unit_of_work.api_keys.create(api_key)
                except ApiKeyRepositoryConflictError as exc:
                    raise IdentityConflictError("API key persistence conflict.") from exc
                await unit_of_work.commit()
        except Exception:
            log_application_event(
                logger,
                event="api_key_create",
                result=AuditResult.FAILURE,
                owner_id=request.owner_id,
                owner_type=request.owner_type,
            )
            await record_audit_event(
                self._audit_recorder,
                request.audit_context,
                action="apikey.create",
                resource_type="api_key",
                resource_id=None,
                result=AuditResult.FAILURE,
                metadata={"owner_id": request.owner_id, "owner_type": request.owner_type},
            )
            raise

        log_application_event(
            logger,
            event="api_key_create",
            result=AuditResult.SUCCESS,
            resource_id=str(created.id),
            owner_id=str(created.owner_id),
            owner_type=created.owner_type.value,
            expires_at_configured=created.expires_at is not None,
        )
        await record_audit_event(
            self._audit_recorder,
            request.audit_context,
            action="apikey.create",
            resource_type="api_key",
            resource_id=str(created.id),
            result=AuditResult.SUCCESS,
            metadata={
                "owner_id": str(created.owner_id),
                "owner_type": created.owner_type.value,
                "key_prefix": created.key_prefix,
            },
        )

        return ApiKeyCreatedResponse.from_domain(created, raw_api_key)

    @staticmethod
    def _validate_owner_type(raw_owner_type: str) -> ApiKeyOwnerType:
        try:
            return ApiKeyOwnerType(raw_owner_type)
        except ValueError as exc:
            raise IdentityValidationError("API key owner type is invalid.") from exc

    @staticmethod
    def _validate_owner_id(
        raw_owner_id: str,
        owner_type: ApiKeyOwnerType,
    ) -> UserId | ServiceAccountId:
        try:
            if owner_type is ApiKeyOwnerType.USER:
                return UserId.from_string(raw_owner_id)
            return ServiceAccountId.from_string(raw_owner_id)
        except ValueError as exc:
            raise IdentityValidationError("API key owner id must be a valid UUID.") from exc

    @staticmethod
    def _validate_expires_at(raw_expires_at: str | None) -> datetime | None:
        if raw_expires_at is None:
            return None
        try:
            parsed = datetime.fromisoformat(raw_expires_at)
        except ValueError as exc:
            raise IdentityValidationError("API key expiration must be a valid datetime.") from exc
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        return parsed

    @staticmethod
    def _validate_name(raw_name: str | None) -> str | None:
        if raw_name is None:
            return None
        name = raw_name.strip()
        if not name:
            raise IdentityValidationError("API key name is required.")
        if len(name) > 120:
            raise IdentityValidationError("API key name must be 120 characters or fewer.")
        return name

    @staticmethod
    def _validate_description(raw_description: str | None) -> str | None:
        if raw_description is None:
            return None
        description = raw_description.strip()
        if not description:
            return None
        if len(description) > 1000:
            raise IdentityValidationError("API key description must be 1000 characters or fewer.")
        return description

    @staticmethod
    def _validate_string_tuple(raw_values: tuple[str, ...], *, field_name: str) -> tuple[str, ...]:
        values = tuple(value.strip() for value in raw_values if value.strip())
        if len(values) > 50:
            raise IdentityValidationError(f"{field_name} must include 50 items or fewer.")
        for value in values:
            if len(value) > 120:
                raise IdentityValidationError(
                    f"{field_name} entries must be 120 characters or fewer."
                )
        return values

    @staticmethod
    async def _ensure_active_owner(
        unit_of_work: IdentityUnitOfWork,
        owner_id: UserId | ServiceAccountId,
        owner_type: ApiKeyOwnerType,
    ) -> None:
        if owner_type is ApiKeyOwnerType.USER:
            if not isinstance(owner_id, UserId):
                raise IdentityValidationError("API key owner id must be a user id.")
            user = await unit_of_work.users.get(owner_id)
            if user is None:
                raise IdentityNotFoundError("API key owner not found.")
            if user.status is not IdentityStatus.ACTIVE:
                raise IdentityNotFoundError("API key owner is not active.")
            return

        if not isinstance(owner_id, ServiceAccountId):
            raise IdentityValidationError("API key owner id must be a service account id.")
        service_account = await unit_of_work.service_accounts.get(owner_id)
        if service_account is None:
            raise IdentityNotFoundError("API key owner not found.")
        if service_account.status is not IdentityStatus.ACTIVE:
            raise IdentityNotFoundError("API key owner is not active.")


class ListApiKeysUseCase:
    _SUPPORTED_STATUSES: ClassVar[set[str]] = {"active", "expired", "revoked", "unknown"}

    def __init__(self, unit_of_work: IdentityUnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def execute(self, request: ListApiKeysRequest) -> ApiKeyListResponse:
        page = self._validate_page(request.page)
        page_size = self._validate_page_size(request.page_size)
        status = self._validate_status(request.status)
        search = request.search.strip() if request.search else None
        offset = (page - 1) * page_size
        now = datetime.now(UTC)

        async with self._unit_of_work as unit_of_work:
            total = await unit_of_work.api_keys.count(search=search, status=status, now=now)
            api_keys = await unit_of_work.api_keys.list(
                limit=page_size,
                offset=offset,
                search=search,
                status=status,
                now=now,
            )

        return ApiKeyListResponse(
            data=tuple(ApiKeyResponse.from_domain(api_key) for api_key in api_keys),
            pagination=ApiKeyPaginationResponse(
                page=page,
                page_size=page_size,
                total=total,
                has_next_page=offset + page_size < total,
                has_previous_page=page > 1,
            ),
            permissions=ApiKeyPermissionsResponse(create=True, read=True, revoke=True, update=True),
        )

    @staticmethod
    def _validate_page(page: int) -> int:
        if page < 1:
            raise IdentityValidationError("Page must be greater than or equal to 1.")
        return page

    @staticmethod
    def _validate_page_size(page_size: int) -> int:
        if page_size < 1 or page_size > 100:
            raise IdentityValidationError("Page size must be between 1 and 100.")
        return page_size

    @classmethod
    def _validate_status(cls, raw_status: str | None) -> str | None:
        if raw_status is None or raw_status.strip() == "":
            return None
        status = raw_status.strip().lower()
        if status not in cls._SUPPORTED_STATUSES:
            raise IdentityValidationError("API key status filter is invalid.")
        return status


class GetApiKeyUseCase:
    def __init__(self, unit_of_work: IdentityUnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def execute(self, request: GetApiKeyRequest) -> ApiKeyResponse:
        try:
            api_key_id = ApiKeyId.from_string(request.api_key_id)
        except ValueError as exc:
            raise IdentityValidationError("API key id must be a valid UUID.") from exc

        async with self._unit_of_work as unit_of_work:
            api_key = await unit_of_work.api_keys.get(api_key_id)
            if api_key is None:
                raise IdentityNotFoundError("API key not found.")

        return ApiKeyResponse.from_domain(api_key)


class RevokeApiKeyUseCase:
    def __init__(
        self,
        unit_of_work: IdentityUnitOfWork,
        audit_recorder: AuditRecorder | None = None,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._audit_recorder = audit_recorder or NoopAuditRecorder()

    async def execute(self, request: RevokeApiKeyRequest) -> ApiKeyResponse:
        try:
            api_key_id = ApiKeyId.from_string(request.api_key_id)
        except ValueError as exc:
            raise IdentityValidationError("API key id must be a valid UUID.") from exc

        async with self._unit_of_work as unit_of_work:
            api_key = await unit_of_work.api_keys.get(api_key_id)
            if api_key is None:
                raise IdentityNotFoundError("API key not found.")
            revoked = await unit_of_work.api_keys.update(api_key.revoke())
            await unit_of_work.commit()

        await record_audit_event(
            self._audit_recorder,
            request.audit_context,
            action="apikey.revoke",
            resource_type="api_key",
            resource_id=str(revoked.id),
            result=AuditResult.SUCCESS,
            metadata={"key_prefix": revoked.key_prefix},
        )
        return ApiKeyResponse.from_domain(revoked)


class UpdateApiKeyUseCase:
    def __init__(
        self,
        unit_of_work: IdentityUnitOfWork,
        audit_recorder: AuditRecorder | None = None,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._audit_recorder = audit_recorder or NoopAuditRecorder()

    async def execute(self, request: UpdateApiKeyRequest) -> ApiKeyResponse:
        try:
            api_key_id = ApiKeyId.from_string(request.api_key_id)
        except ValueError as exc:
            raise IdentityValidationError("API key id must be a valid UUID.") from exc

        name = CreateApiKeyUseCase._validate_name(request.name)
        description = CreateApiKeyUseCase._validate_description(request.description)
        expires_at = CreateApiKeyUseCase._validate_expires_at(request.expires_at)
        granted_permissions = CreateApiKeyUseCase._validate_string_tuple(
            request.granted_permissions,
            field_name="API key permissions",
        )
        scopes = CreateApiKeyUseCase._validate_string_tuple(
            request.scopes,
            field_name="API key scopes",
        )

        async with self._unit_of_work as unit_of_work:
            api_key = await unit_of_work.api_keys.get(api_key_id)
            if api_key is None:
                raise IdentityNotFoundError("API key not found.")
            updated = await unit_of_work.api_keys.update(
                api_key.update_metadata(
                    name=name,
                    description=description,
                    granted_permissions=granted_permissions,
                    scopes=scopes,
                    expires_at=expires_at,
                )
            )
            await unit_of_work.commit()

        await record_audit_event(
            self._audit_recorder,
            request.audit_context,
            action="apikey.update",
            resource_type="api_key",
            resource_id=str(updated.id),
            result=AuditResult.SUCCESS,
            metadata={"key_prefix": updated.key_prefix},
        )
        return ApiKeyResponse.from_domain(updated)


class AuthenticateApiKeyUseCase:
    def __init__(
        self,
        unit_of_work: IdentityUnitOfWork,
        api_key_generator: ApiKeySecretGenerator,
        api_key_hasher: ApiKeyHasher,
        audit_recorder: AuditRecorder | None = None,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._api_key_generator = api_key_generator
        self._api_key_hasher = api_key_hasher
        self._audit_recorder = audit_recorder or NoopAuditRecorder()

    async def execute(
        self,
        raw_api_key: str,
        audit_context: AuditContext | None = None,
    ) -> AuthenticatedIdentityResponse:
        key_prefix = self._api_key_generator.extract_prefix(raw_api_key)
        if key_prefix is None:
            log_application_event(
                logger,
                event="api_key_authenticate",
                result=AuditResult.FAILURE,
                reason="invalid_prefix",
            )
            await record_audit_event(
                self._audit_recorder,
                audit_context,
                action="login.failure",
                resource_type="api_key",
                resource_id=None,
                result=AuditResult.FAILURE,
                metadata={"reason": "invalid_prefix"},
            )
            raise AuthenticationFailedError("Invalid API key.")

        try:
            async with self._unit_of_work as unit_of_work:
                api_key = await unit_of_work.api_keys.get_by_prefix(key_prefix)
                if api_key is None:
                    raise AuthenticationFailedError("Invalid API key.")
                if not self._api_key_hasher.verify(raw_api_key, api_key.hashed_key):
                    raise AuthenticationFailedError("Invalid API key.")
                if api_key.is_revoked():
                    raise AuthenticationFailedError("Invalid API key.")
                if api_key.is_expired(datetime.now(UTC)):
                    raise AuthenticationFailedError("Invalid API key.")
                await CreateApiKeyUseCase._ensure_active_owner(
                    unit_of_work,
                    api_key.owner_id,
                    api_key.owner_type,
                )
        except Exception:
            log_application_event(
                logger,
                event="api_key_authenticate",
                result=AuditResult.FAILURE,
                reason="invalid_key",
            )
            await record_audit_event(
                self._audit_recorder,
                audit_context,
                action="login.failure",
                resource_type="api_key",
                resource_id=None,
                result=AuditResult.FAILURE,
                metadata={"key_prefix": key_prefix},
            )
            raise

        authenticated = AuthenticatedIdentityResponse(
            id=str(api_key.owner_id),
            type=api_key.owner_type.value,
            api_key_id=str(api_key.id),
        )
        log_application_event(
            logger,
            event="api_key_authenticate",
            result=AuditResult.SUCCESS,
            resource_id=authenticated.api_key_id,
            owner_id=authenticated.id,
            owner_type=authenticated.type,
        )
        await record_audit_event(
            self._audit_recorder,
            AuditContext(
                actor_id=authenticated.id,
                actor_type=authenticated.type,
                ip_address=audit_context.ip_address if audit_context is not None else None,
                user_agent=audit_context.user_agent if audit_context is not None else None,
                request_id=audit_context.request_id if audit_context is not None else None,
                protocol=audit_context.protocol if audit_context is not None else "rest",
            ),
            action="login.success",
            resource_type="api_key",
            resource_id=authenticated.api_key_id,
            result=AuditResult.SUCCESS,
            metadata={"key_prefix": api_key.key_prefix},
        )

        return authenticated


class CreateSessionUseCase:
    _SESSION_TTL_SECONDS = 12 * 60 * 60

    def __init__(
        self,
        unit_of_work: IdentityUnitOfWork,
        api_key_generator: ApiKeySecretGenerator,
        api_key_hasher: ApiKeyHasher,
        session_token_generator: SessionTokenGenerator,
        session_token_hasher: ApiKeyHasher,
        audit_recorder: AuditRecorder | None = None,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._api_key_generator = api_key_generator
        self._api_key_hasher = api_key_hasher
        self._session_token_generator = session_token_generator
        self._session_token_hasher = session_token_hasher
        self._audit_recorder = audit_recorder or NoopAuditRecorder()

    async def execute(self, request: CreateSessionRequest) -> SessionCreatedResponse:
        raw_api_key = request.api_key.strip()
        key_prefix = self._api_key_generator.extract_prefix(raw_api_key)
        if key_prefix is None:
            await self._record_failure(request.audit_context, "invalid_prefix")
            raise AuthenticationFailedError("Invalid API key.")

        raw_session_token = self._session_token_generator.generate()
        token_prefix = self._session_token_generator.extract_prefix(raw_session_token)
        if token_prefix is None:
            raise IdentityValidationError("Generated session token prefix is invalid.")

        expires_at = datetime.now(UTC) + timedelta(seconds=self._SESSION_TTL_SECONDS)
        try:
            async with self._unit_of_work as unit_of_work:
                api_key = await self._authenticate_api_key(unit_of_work, raw_api_key, key_prefix)
                if api_key.expires_at is not None and api_key.expires_at < expires_at:
                    expires_at = api_key.expires_at
                auth_session = AuthSession.create(
                    hashed_token=self._session_token_hasher.hash(raw_session_token),
                    token_prefix=token_prefix,
                    api_key_id=api_key.id,
                    owner_id=api_key.owner_id,
                    owner_type=api_key.owner_type,
                    expires_at=expires_at,
                )
                created = await unit_of_work.auth_sessions.create(auth_session)
                current_session = await build_current_session_response(unit_of_work, created)
                await unit_of_work.commit()
        except Exception:
            await self._record_failure(request.audit_context, "invalid_key")
            raise

        await record_audit_event(
            self._audit_recorder,
            AuditContext(
                actor_id=str(created.owner_id),
                actor_type=created.owner_type.value,
                ip_address=request.audit_context.ip_address if request.audit_context else None,
                user_agent=request.audit_context.user_agent if request.audit_context else None,
                request_id=request.audit_context.request_id if request.audit_context else None,
                protocol=request.audit_context.protocol if request.audit_context else "rest",
            ),
            action="session.create",
            resource_type="auth_session",
            resource_id=str(created.id),
            result=AuditResult.SUCCESS,
            metadata={"api_key_id": str(created.api_key_id), "token_prefix": created.token_prefix},
        )

        return SessionCreatedResponse(session_token=raw_session_token, session=current_session)

    async def _authenticate_api_key(
        self,
        unit_of_work: IdentityUnitOfWork,
        raw_api_key: str,
        key_prefix: str,
    ) -> ApiKey:
        api_key = await unit_of_work.api_keys.get_by_prefix(key_prefix)
        if api_key is None:
            raise AuthenticationFailedError("Invalid API key.")
        if not self._api_key_hasher.verify(raw_api_key, api_key.hashed_key):
            raise AuthenticationFailedError("Invalid API key.")
        if api_key.is_revoked() or api_key.is_expired(datetime.now(UTC)):
            raise AuthenticationFailedError("Invalid API key.")
        await CreateApiKeyUseCase._ensure_active_owner(
            unit_of_work,
            api_key.owner_id,
            api_key.owner_type,
        )
        return api_key

    async def _record_failure(self, audit_context: AuditContext | None, reason: str) -> None:
        log_application_event(
            logger,
            event="session_create",
            result=AuditResult.FAILURE,
            reason=reason,
        )
        await record_audit_event(
            self._audit_recorder,
            audit_context,
            action="session.create",
            resource_type="auth_session",
            resource_id=None,
            result=AuditResult.FAILURE,
            metadata={"reason": reason},
        )


class AuthenticateSessionUseCase:
    def __init__(
        self,
        unit_of_work: IdentityUnitOfWork,
        session_token_generator: SessionTokenGenerator,
        session_token_hasher: ApiKeyHasher,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._session_token_generator = session_token_generator
        self._session_token_hasher = session_token_hasher

    async def execute(self, raw_session_token: str) -> AuthenticatedIdentityResponse:
        token_prefix = self._session_token_generator.extract_prefix(raw_session_token)
        if token_prefix is None:
            raise AuthenticationFailedError("Invalid session.")

        async with self._unit_of_work as unit_of_work:
            auth_session = await unit_of_work.auth_sessions.get_by_prefix(token_prefix)
            if auth_session is None:
                raise AuthenticationFailedError("Invalid session.")
            if not self._session_token_hasher.verify(
                raw_session_token,
                auth_session.hashed_token,
            ):
                raise AuthenticationFailedError("Invalid session.")
            if auth_session.is_revoked() or auth_session.is_expired(datetime.now(UTC)):
                raise AuthenticationFailedError("Invalid session.")
            api_key = await unit_of_work.api_keys.get(auth_session.api_key_id)
            if api_key is None or api_key.is_revoked() or api_key.is_expired(datetime.now(UTC)):
                raise AuthenticationFailedError("Invalid session.")
            await CreateApiKeyUseCase._ensure_active_owner(
                unit_of_work,
                auth_session.owner_id,
                auth_session.owner_type,
            )
            updated = auth_session.mark_seen()
            await unit_of_work.auth_sessions.update(updated)
            await unit_of_work.commit()

        return AuthenticatedIdentityResponse(
            id=str(auth_session.owner_id),
            type=auth_session.owner_type.value,
            api_key_id=str(auth_session.api_key_id),
            session_id=str(auth_session.id),
        )


class GetCurrentSessionUseCase:
    def __init__(self, unit_of_work: IdentityUnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def execute(
        self,
        api_key_id: str,
        session_id: str | None = None,
    ) -> CurrentSessionResponse:
        async with self._unit_of_work as unit_of_work:
            if session_id is not None:
                auth_session = await unit_of_work.auth_sessions.get(
                    SessionId.from_string(session_id)
                )
                if auth_session is None or auth_session.is_revoked():
                    raise AuthenticationFailedError("Invalid session.")
                return await build_current_session_response(unit_of_work, auth_session)

            api_key = await unit_of_work.api_keys.get(ApiKeyId.from_string(api_key_id))
            if api_key is None:
                raise AuthenticationFailedError("Invalid session.")
            return await build_current_session_response(unit_of_work, api_key)


class RevokeCurrentSessionUseCase:
    def __init__(
        self,
        unit_of_work: IdentityUnitOfWork,
        audit_recorder: AuditRecorder | None = None,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._audit_recorder = audit_recorder or NoopAuditRecorder()

    async def execute(
        self,
        session_id: str | None,
        audit_context: AuditContext | None = None,
    ) -> None:
        if session_id is None:
            return

        async with self._unit_of_work as unit_of_work:
            auth_session = await unit_of_work.auth_sessions.get(SessionId.from_string(session_id))
            if auth_session is None:
                return
            revoked = auth_session.revoke()
            await unit_of_work.auth_sessions.update(revoked)
            await unit_of_work.commit()

        await record_audit_event(
            self._audit_recorder,
            AuditContext(
                actor_id=str(revoked.owner_id),
                actor_type=revoked.owner_type.value,
                ip_address=audit_context.ip_address if audit_context else None,
                user_agent=audit_context.user_agent if audit_context else None,
                request_id=audit_context.request_id if audit_context else None,
                protocol=audit_context.protocol if audit_context else "rest",
            ),
            action="session.revoke",
            resource_type="auth_session",
            resource_id=str(revoked.id),
            result=AuditResult.SUCCESS,
            metadata={"api_key_id": str(revoked.api_key_id)},
        )


async def build_current_session_response(
    unit_of_work: IdentityUnitOfWork,
    auth: AuthSession | ApiKey,
) -> CurrentSessionResponse:
    owner_id = auth.owner_id
    owner_type = auth.owner_type
    if owner_type is ApiKeyOwnerType.USER:
        if not isinstance(owner_id, UserId):
            raise IdentityValidationError("Session owner id must be a user id.")
        user = await unit_of_work.users.get(owner_id)
        if user is None:
            raise AuthenticationFailedError("Invalid session.")
        return CurrentSessionResponse(
            api_key_id=str(auth.api_key_id if isinstance(auth, AuthSession) else auth.id),
            auth_method="api_key",
            expires_at=auth.expires_at.isoformat() if auth.expires_at is not None else None,
            issued_at=auth.created_at.isoformat(),
            user_id=str(user.id),
            user_type=owner_type.value,
            email=user.email.value,
            name=user.display_name.value,
            profile_label="User",
        )

    if not isinstance(owner_id, ServiceAccountId):
        raise IdentityValidationError("Session owner id must be a service account id.")
    service_account = await unit_of_work.service_accounts.get(owner_id)
    if service_account is None:
        raise AuthenticationFailedError("Invalid session.")
    return CurrentSessionResponse(
        api_key_id=str(auth.api_key_id if isinstance(auth, AuthSession) else auth.id),
        auth_method="api_key",
        expires_at=auth.expires_at.isoformat() if auth.expires_at is not None else None,
        issued_at=auth.created_at.isoformat(),
        user_id=str(service_account.id),
        user_type=owner_type.value,
        email=None,
        name=service_account.name.value,
        profile_label="Service account",
    )

from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta
from typing import ClassVar

from application.audit.dto import AuditContext
from application.audit.use_cases import NoopAuditRecorder, record_audit_event
from application.identity.dto import (
    AccountSecurityResponse,
    ActiveSessionListResponse,
    ActiveSessionResponse,
    ApiKeyCreatedResponse,
    ApiKeyListResponse,
    ApiKeyPaginationResponse,
    ApiKeyPermissionsResponse,
    ApiKeyResponse,
    AuthenticatedIdentityResponse,
    ChangePasswordRequest,
    CreateApiKeyRequest,
    CreateServiceAccountRequest,
    CreateSessionRequest,
    CreateUserRequest,
    CurrentSessionResponse,
    GetApiKeyRequest,
    GetProfileRequest,
    GetSettingsRequest,
    ListActiveSessionsRequest,
    ListApiKeysRequest,
    NotificationPreferencesResponse,
    ProfilePermissionsResponse,
    PublicSettingsResponse,
    RevokeApiKeyRequest,
    RevokeSessionRequest,
    ServiceAccountResponse,
    SessionCreatedResponse,
    SettingsPermissionsResponse,
    SettingsResponse,
    UpdateApiKeyRequest,
    UpdateNotificationsRequest,
    UpdatePreferencesRequest,
    UpdateProfileRequest,
    UserPreferencesResponse,
    UserProfileResponse,
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
from domain.identity.entities import ApiKey, AuthSession, ServiceAccount, User, UserPreferences
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
        try:
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
        except Exception:
            log_application_event(
                logger,
                event="service_account_create",
                result=AuditResult.FAILURE,
                project_id=request.project_id,
            )
            raise

        log_application_event(
            logger,
            event="service_account_create",
            result=AuditResult.SUCCESS,
            resource_id=str(created.id),
            project_id=str(created.project_id),
            description_configured=created.description is not None,
        )

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
        log_application_event(
            logger,
            event="api_key_revoke",
            result=AuditResult.SUCCESS,
            resource_id=str(revoked.id),
            owner_id=str(revoked.owner_id),
            owner_type=revoked.owner_type.value,
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
        log_application_event(
            logger,
            event="api_key_update",
            result=AuditResult.SUCCESS,
            resource_id=str(updated.id),
            owner_id=str(updated.owner_id),
            owner_type=updated.owner_type.value,
            expires_at_configured=updated.expires_at is not None,
            permissions_count=len(updated.granted_permissions),
            scopes_count=len(updated.scopes),
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
        log_application_event(
            logger,
            event="session_create",
            result=AuditResult.SUCCESS,
            resource_id=str(created.id),
            owner_id=str(created.owner_id),
            owner_type=created.owner_type.value,
            credential_id=str(created.api_key_id),
            expires_at_configured=True,
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
            log_application_event(
                logger,
                event="session_authenticate",
                result=AuditResult.FAILURE,
                reason="invalid_prefix",
            )
            raise AuthenticationFailedError("Invalid session.")

        try:
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
                if api_key is None or api_key.is_revoked() or api_key.is_expired(
                    datetime.now(UTC)
                ):
                    raise AuthenticationFailedError("Invalid session.")
                await CreateApiKeyUseCase._ensure_active_owner(
                    unit_of_work,
                    auth_session.owner_id,
                    auth_session.owner_type,
                )
                updated = auth_session.mark_seen()
                await unit_of_work.auth_sessions.update(updated)
                await unit_of_work.commit()
        except Exception:
            log_application_event(
                logger,
                event="session_authenticate",
                result=AuditResult.FAILURE,
                reason="invalid_session",
            )
            raise

        log_application_event(
            logger,
            event="session_authenticate",
            result=AuditResult.SUCCESS,
            resource_id=str(auth_session.id),
            owner_id=str(auth_session.owner_id),
            owner_type=auth_session.owner_type.value,
            credential_id=str(auth_session.api_key_id),
        )

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
        log_application_event(
            logger,
            event="session_revoke_current",
            result=AuditResult.SUCCESS,
            resource_id=str(revoked.id),
            owner_id=str(revoked.owner_id),
            owner_type=revoked.owner_type.value,
            credential_id=str(revoked.api_key_id),
        )


class GetCurrentProfileUseCase:
    def __init__(self, unit_of_work: IdentityUnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def execute(self, request: GetProfileRequest) -> UserProfileResponse:
        identity_type = _validate_owner_type(request.identity_type)
        identity_id = _validate_owner_id(request.identity_id, identity_type)
        async with self._unit_of_work as unit_of_work:
            response = await _build_profile_response(unit_of_work, identity_id, identity_type)
            await unit_of_work.commit()
            return response


class UpdateCurrentProfileUseCase:
    def __init__(
        self,
        unit_of_work: IdentityUnitOfWork,
        audit_recorder: AuditRecorder | None = None,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._audit_recorder = audit_recorder or NoopAuditRecorder()

    async def execute(self, request: UpdateProfileRequest) -> UserProfileResponse:
        identity_type = _validate_owner_type(request.identity_type)
        identity_id = _validate_owner_id(request.identity_id, identity_type)
        if identity_type is not ApiKeyOwnerType.USER or not isinstance(identity_id, UserId):
            raise IdentityValidationError("Only user profiles can be updated.")
        display_name = _validate_display_name(request.name)
        organization = _validate_optional_text(
            request.organization,
            field_name="Organization",
            max_length=120,
        )

        async with self._unit_of_work as unit_of_work:
            user = await unit_of_work.users.get(identity_id)
            if user is None or user.status is not IdentityStatus.ACTIVE:
                raise IdentityNotFoundError("Profile not found.")
            if request.email is not None and _validate_email(request.email) != user.email:
                raise IdentityValidationError("User email cannot be changed from profile settings.")
            await unit_of_work.users.update(user.update_display_name(display_name))
            preferences = await _get_or_create_preferences(unit_of_work, identity_id)
            await unit_of_work.user_preferences.upsert(
                preferences.update_profile_metadata(organization=organization)
            )
            await unit_of_work.commit()
            response = await _build_profile_response(unit_of_work, identity_id, identity_type)

        await record_audit_event(
            self._audit_recorder,
            request.audit_context,
            action="profile.update",
            resource_type="user",
            resource_id=request.identity_id,
            result=AuditResult.SUCCESS,
        )
        log_application_event(
            logger,
            event="profile_update",
            result=AuditResult.SUCCESS,
            resource_id=request.identity_id,
            identity_type=request.identity_type,
            organization_configured=organization is not None,
        )
        return response


class GetAccountSecurityUseCase:
    async def execute(self) -> AccountSecurityResponse:
        return AccountSecurityResponse(
            mfa_enabled=False,
            passkeys_enabled=False,
            password_change_available=False,
            recovery_keys_available=False,
            webauthn_enabled=False,
        )


class ListActiveSessionsUseCase:
    def __init__(self, unit_of_work: IdentityUnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def execute(self, request: ListActiveSessionsRequest) -> ActiveSessionListResponse:
        identity_type = _validate_owner_type(request.identity_type)
        identity_id = _validate_owner_id(request.identity_id, identity_type)
        async with self._unit_of_work as unit_of_work:
            sessions = await unit_of_work.auth_sessions.list_for_owner(
                identity_id,
                identity_type,
            )
        return ActiveSessionListResponse(
            data=tuple(
                ActiveSessionResponse.from_domain(
                    session,
                    current_session_id=request.current_session_id,
                )
                for session in sessions
            ),
            permissions=_profile_permissions(),
        )


class RevokeSessionUseCase:
    def __init__(
        self,
        unit_of_work: IdentityUnitOfWork,
        audit_recorder: AuditRecorder | None = None,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._audit_recorder = audit_recorder or NoopAuditRecorder()

    async def execute(self, request: RevokeSessionRequest) -> None:
        identity_type = _validate_owner_type(request.identity_type)
        identity_id = _validate_owner_id(request.identity_id, identity_type)
        try:
            session_id = SessionId.from_string(request.session_id)
        except ValueError as exc:
            raise IdentityValidationError("Session id must be a valid UUID.") from exc

        async with self._unit_of_work as unit_of_work:
            auth_session = await unit_of_work.auth_sessions.get(session_id)
            if auth_session is None:
                raise IdentityNotFoundError("Session not found.")
            if auth_session.owner_id != identity_id or auth_session.owner_type is not identity_type:
                raise IdentityNotFoundError("Session not found.")
            if auth_session.revoked_at is None:
                revoked = auth_session.revoke()
                await unit_of_work.auth_sessions.update(revoked)
                await unit_of_work.commit()
            else:
                revoked = auth_session

        await record_audit_event(
            self._audit_recorder,
            request.audit_context,
            action="session.revoke",
            resource_type="auth_session",
            resource_id=str(revoked.id),
            result=AuditResult.SUCCESS,
        )
        log_application_event(
            logger,
            event="session_revoke",
            result=AuditResult.SUCCESS,
            resource_id=str(revoked.id),
            owner_id=str(revoked.owner_id),
            owner_type=revoked.owner_type.value,
        )


class ChangePasswordUseCase:
    async def execute(self, request: ChangePasswordRequest) -> None:
        _validate_owner_type(request.identity_type)
        if not request.current_password or not request.new_password:
            raise IdentityValidationError("Password data is required.")
        raise IdentityValidationError("Password authentication is not configured.")


class GetSettingsUseCase:
    def __init__(
        self,
        unit_of_work: IdentityUnitOfWork,
        *,
        service_name: str = "mcp-secret-manager",
        environment: str | None = None,
        backend_version: str | None = "0.1.0",
    ) -> None:
        self._unit_of_work = unit_of_work
        self._service_name = service_name
        self._environment = environment
        self._backend_version = backend_version

    async def execute(self, request: GetSettingsRequest) -> SettingsResponse:
        identity_type = _validate_owner_type(request.identity_type)
        identity_id = _validate_owner_id(request.identity_id, identity_type)
        if identity_type is not ApiKeyOwnerType.USER or not isinstance(identity_id, UserId):
            preferences = UserPreferences.default(UserId.new())
            return _settings_response(
                preferences,
                service_name=self._service_name,
                environment=self._environment,
                backend_version=self._backend_version,
                editable=False,
            )

        async with self._unit_of_work as unit_of_work:
            preferences = await _get_or_create_preferences(unit_of_work, identity_id)
            await unit_of_work.commit()
        return _settings_response(
            preferences,
            service_name=self._service_name,
            environment=self._environment,
            backend_version=self._backend_version,
            editable=True,
        )


class UpdatePreferencesUseCase:
    def __init__(
        self,
        unit_of_work: IdentityUnitOfWork,
        audit_recorder: AuditRecorder | None = None,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._audit_recorder = audit_recorder or NoopAuditRecorder()

    async def execute(self, request: UpdatePreferencesRequest) -> UserPreferencesResponse:
        identity_type = _validate_owner_type(request.identity_type)
        identity_id = _validate_owner_id(request.identity_id, identity_type)
        if identity_type is not ApiKeyOwnerType.USER or not isinstance(identity_id, UserId):
            raise IdentityValidationError("Only user preferences can be updated.")
        theme = _validate_choice(request.theme, {"light", "dark", "system"}, "Theme")
        language = _validate_choice(request.language, {"en", "fr"}, "Language")
        date_time_format = _validate_choice(
            request.date_time_format,
            {"absolute", "relative", "short"},
            "Date/time format",
        )
        display_density = _validate_choice(
            request.display_density,
            {"comfortable", "compact"},
            "Display density",
        )
        timezone = _validate_optional_text(request.timezone, field_name="Timezone", max_length=80)
        if timezone is None:
            raise IdentityValidationError("Timezone is required.")

        async with self._unit_of_work as unit_of_work:
            preferences = await _get_or_create_preferences(unit_of_work, identity_id)
            updated = await unit_of_work.user_preferences.upsert(
                preferences.update_preferences(
                    theme=theme,
                    language=language,
                    timezone=timezone,
                    date_time_format=date_time_format,
                    display_density=display_density,
                )
            )
            await unit_of_work.commit()

        await record_audit_event(
            self._audit_recorder,
            request.audit_context,
            action="settings.preferences.update",
            resource_type="user_preferences",
            resource_id=request.identity_id,
            result=AuditResult.SUCCESS,
        )
        log_application_event(
            logger,
            event="settings_preferences_update",
            result=AuditResult.SUCCESS,
            resource_id=request.identity_id,
            identity_type=request.identity_type,
            theme=request.theme,
            language=request.language,
            timezone_configured=timezone is not None,
        )
        return UserPreferencesResponse.from_domain(updated)


class UpdateNotificationsUseCase:
    def __init__(
        self,
        unit_of_work: IdentityUnitOfWork,
        audit_recorder: AuditRecorder | None = None,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._audit_recorder = audit_recorder or NoopAuditRecorder()

    async def execute(
        self,
        request: UpdateNotificationsRequest,
    ) -> NotificationPreferencesResponse:
        identity_type = _validate_owner_type(request.identity_type)
        identity_id = _validate_owner_id(request.identity_id, identity_type)
        if identity_type is not ApiKeyOwnerType.USER or not isinstance(identity_id, UserId):
            raise IdentityValidationError("Only user notifications can be updated.")

        async with self._unit_of_work as unit_of_work:
            preferences = await _get_or_create_preferences(unit_of_work, identity_id)
            updated = await unit_of_work.user_preferences.upsert(
                preferences.update_notifications(
                    audit_alerts=request.audit_alerts,
                    email_enabled=request.email_enabled,
                    in_app_enabled=request.in_app_enabled,
                    product_updates=request.product_updates,
                    security_alerts=request.security_alerts,
                )
            )
            await unit_of_work.commit()

        await record_audit_event(
            self._audit_recorder,
            request.audit_context,
            action="settings.notifications.update",
            resource_type="user_preferences",
            resource_id=request.identity_id,
            result=AuditResult.SUCCESS,
        )
        log_application_event(
            logger,
            event="settings_notifications_update",
            result=AuditResult.SUCCESS,
            resource_id=request.identity_id,
            identity_type=request.identity_type,
            audit_alerts_enabled=request.audit_alerts,
            email_enabled=request.email_enabled,
            in_app_enabled=request.in_app_enabled,
            security_alerts_enabled=request.security_alerts,
        )
        return NotificationPreferencesResponse.from_domain(updated)


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


async def _build_profile_response(
    unit_of_work: IdentityUnitOfWork,
    identity_id: UserId | ServiceAccountId,
    identity_type: ApiKeyOwnerType,
) -> UserProfileResponse:
    if identity_type is ApiKeyOwnerType.USER:
        if not isinstance(identity_id, UserId):
            raise IdentityValidationError("Profile id must be a user id.")
        user = await unit_of_work.users.get(identity_id)
        if user is None or user.status is not IdentityStatus.ACTIVE:
            raise IdentityNotFoundError("Profile not found.")
        preferences = await _get_or_create_preferences(unit_of_work, identity_id)
        return UserProfileResponse(
            id=str(user.id),
            email=user.email.value,
            name=user.display_name.value,
            account_type="human",
            avatar_url=preferences.avatar_url,
            organization=preferences.organization,
            email_editable=False,
            primary_role=None,
            last_login_at=None,
            created_at=user.created_at.isoformat(),
            permissions=_profile_permissions(),
        )

    if not isinstance(identity_id, ServiceAccountId):
        raise IdentityValidationError("Profile id must be a service account id.")
    service_account = await unit_of_work.service_accounts.get(identity_id)
    if service_account is None or service_account.status is not IdentityStatus.ACTIVE:
        raise IdentityNotFoundError("Profile not found.")
    return UserProfileResponse(
        id=str(service_account.id),
        email=None,
        name=service_account.name.value,
        account_type="service",
        avatar_url=None,
        organization=None,
        email_editable=False,
        primary_role=None,
        last_login_at=None,
        created_at=service_account.created_at.isoformat(),
        permissions=ProfilePermissionsResponse(
            change_password=False,
            read=True,
            revoke_sessions=False,
            update=False,
        ),
    )


async def _get_or_create_preferences(
    unit_of_work: IdentityUnitOfWork,
    user_id: UserId,
) -> UserPreferences:
    preferences = await unit_of_work.user_preferences.get(user_id)
    if preferences is not None:
        return preferences
    return await unit_of_work.user_preferences.upsert(UserPreferences.default(user_id))


def _profile_permissions() -> ProfilePermissionsResponse:
    return ProfilePermissionsResponse(
        change_password=False,
        read=True,
        revoke_sessions=True,
        update=True,
    )


def _settings_response(
    preferences: UserPreferences,
    *,
    service_name: str,
    environment: str | None,
    backend_version: str | None,
    editable: bool,
) -> SettingsResponse:
    return SettingsResponse(
        notifications=NotificationPreferencesResponse.from_domain(preferences),
        permissions=SettingsPermissionsResponse(
            read=True,
            update=editable,
            update_notifications=editable,
            update_preferences=editable,
        ),
        preferences=UserPreferencesResponse.from_domain(preferences),
        public_settings=PublicSettingsResponse(
            api_status="healthy",
            backend_version=backend_version,
            deployment_mode=None,
            environment=environment,
            frontend_version=None,
            instance_name=service_name,
            public_url=None,
        ),
    )


def _validate_owner_type(raw_owner_type: str) -> ApiKeyOwnerType:
    try:
        return ApiKeyOwnerType(raw_owner_type)
    except ValueError as exc:
        raise IdentityValidationError("Identity type is invalid.") from exc


def _validate_owner_id(
    raw_owner_id: str,
    owner_type: ApiKeyOwnerType,
) -> UserId | ServiceAccountId:
    try:
        if owner_type is ApiKeyOwnerType.USER:
            return UserId.from_string(raw_owner_id)
        return ServiceAccountId.from_string(raw_owner_id)
    except ValueError as exc:
        raise IdentityValidationError("Identity id must be a valid UUID.") from exc


def _validate_display_name(raw_display_name: str) -> UserDisplayName:
    try:
        return UserDisplayName(raw_display_name)
    except IdentityDomainError as exc:
        raise IdentityValidationError(str(exc)) from exc


def _validate_email(raw_email: str) -> UserEmail:
    try:
        return UserEmail(raw_email)
    except IdentityDomainError as exc:
        raise IdentityValidationError(str(exc)) from exc


def _validate_optional_text(
    raw_value: str | None,
    *,
    field_name: str,
    max_length: int,
) -> str | None:
    if raw_value is None:
        return None
    value = raw_value.strip()
    if not value:
        return None
    if len(value) > max_length:
        raise IdentityValidationError(f"{field_name} must be {max_length} characters or fewer.")
    return value


def _validate_choice(raw_value: str, choices: set[str], field_name: str) -> str:
    value = raw_value.strip().lower()
    if value not in choices:
        raise IdentityValidationError(f"{field_name} is invalid.")
    return value

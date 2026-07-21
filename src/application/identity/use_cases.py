from __future__ import annotations

from datetime import UTC, datetime

from application.identity.dto import (
    ApiKeyCreatedResponse,
    AuthenticatedIdentityResponse,
    CreateApiKeyRequest,
    CreateServiceAccountRequest,
    CreateUserRequest,
    ServiceAccountResponse,
    UserResponse,
)
from application.identity.exceptions import (
    AuthenticationFailedError,
    IdentityConflictError,
    IdentityNotFoundError,
    IdentityValidationError,
)
from application.identity.unit_of_work import IdentityUnitOfWork
from domain.identity.entities import ApiKey, ServiceAccount, User
from domain.identity.exceptions import IdentityDomainError
from domain.identity.repositories import (
    ApiKeyRepositoryConflictError,
    ServiceAccountRepositoryConflictError,
    UserRepositoryConflictError,
)
from domain.identity.services import ApiKeyHasher, ApiKeySecretGenerator
from domain.identity.value_objects import (
    ApiKeyOwnerType,
    IdentityStatus,
    ServiceAccountId,
    ServiceAccountName,
    UserDisplayName,
    UserEmail,
    UserId,
)
from domain.project.value_objects import ProjectId


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
    ) -> None:
        self._unit_of_work = unit_of_work
        self._api_key_generator = api_key_generator
        self._api_key_hasher = api_key_hasher

    async def execute(self, request: CreateApiKeyRequest) -> ApiKeyCreatedResponse:
        owner_type = self._validate_owner_type(request.owner_type)
        owner_id = self._validate_owner_id(request.owner_id, owner_type)
        expires_at = self._validate_expires_at(request.expires_at)
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
            )
            try:
                created = await unit_of_work.api_keys.create(api_key)
            except ApiKeyRepositoryConflictError as exc:
                raise IdentityConflictError("API key persistence conflict.") from exc
            await unit_of_work.commit()

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


class AuthenticateApiKeyUseCase:
    def __init__(
        self,
        unit_of_work: IdentityUnitOfWork,
        api_key_generator: ApiKeySecretGenerator,
        api_key_hasher: ApiKeyHasher,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._api_key_generator = api_key_generator
        self._api_key_hasher = api_key_hasher

    async def execute(self, raw_api_key: str) -> AuthenticatedIdentityResponse:
        key_prefix = self._api_key_generator.extract_prefix(raw_api_key)
        if key_prefix is None:
            raise AuthenticationFailedError("Invalid API key.")

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

        return AuthenticatedIdentityResponse(
            id=str(api_key.owner_id),
            type=api_key.owner_type.value,
            api_key_id=str(api_key.id),
        )

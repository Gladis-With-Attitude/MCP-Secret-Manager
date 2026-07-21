from __future__ import annotations

from collections.abc import Sequence

from application.secret_version.dto import CreateSecretVersionRequest, SecretVersionResponse
from application.secret_version.exceptions import (
    SecretNotFoundError,
    SecretVersionConflictError,
    SecretVersionNotFoundError,
    SecretVersionValidationError,
)
from application.unit_of_work import UnitOfWork
from domain.secret.value_objects import SecretId
from domain.secret_version.entities import SecretVersion
from domain.secret_version.exceptions import SecretVersionDomainError
from domain.secret_version.repositories import SecretVersionRepositoryConflictError
from domain.secret_version.value_objects import SecretValue, SecretVersionNumber


class CreateSecretVersionUseCase:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def execute(self, request: CreateSecretVersionRequest) -> SecretVersionResponse:
        secret_id = self._validate_secret_id(request.secret_id)
        value = self._validate_value(request.value)

        async with self._unit_of_work as unit_of_work:
            secret = await unit_of_work.secrets.get(secret_id)
            if secret is None:
                raise SecretNotFoundError("Secret not found.")

            versions = await unit_of_work.secret_versions.list_versions(secret_id)
            next_version = self._next_version_number(versions)
            secret_version = SecretVersion.create(
                secret_id=secret_id,
                value=value,
                version=next_version,
            )

            try:
                await unit_of_work.secret_versions.deactivate_previous_versions(secret_id)
                created_secret_version = await unit_of_work.secret_versions.create(secret_version)
            except SecretVersionRepositoryConflictError as exc:
                raise SecretVersionConflictError("Secret version persistence conflict.") from exc

            await unit_of_work.commit()

        return SecretVersionResponse.from_domain(created_secret_version)

    @staticmethod
    def _next_version_number(versions: Sequence[SecretVersion]) -> SecretVersionNumber:
        if not versions:
            return SecretVersionNumber(1)
        latest_version_number = max(secret_version.version.value for secret_version in versions)
        return SecretVersionNumber(latest_version_number + 1)

    @staticmethod
    def _validate_secret_id(raw_secret_id: str) -> SecretId:
        try:
            return SecretId.from_string(raw_secret_id)
        except ValueError as exc:
            raise SecretVersionValidationError("Secret id must be a valid UUID.") from exc

    @staticmethod
    def _validate_value(raw_value: str) -> SecretValue:
        try:
            return SecretValue(raw_value)
        except SecretVersionDomainError as exc:
            raise SecretVersionValidationError(str(exc)) from exc


class ListSecretVersionsUseCase:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def execute(self, secret_id: str) -> tuple[SecretVersionResponse, ...]:
        validated_secret_id = CreateSecretVersionUseCase._validate_secret_id(secret_id)

        async with self._unit_of_work as unit_of_work:
            secret = await unit_of_work.secrets.get(validated_secret_id)
            if secret is None:
                raise SecretNotFoundError("Secret not found.")

            versions = await unit_of_work.secret_versions.list_versions(validated_secret_id)

        return tuple(SecretVersionResponse.from_domain(version) for version in versions)


class GetActiveSecretVersionUseCase:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def execute(self, secret_id: str) -> SecretVersionResponse:
        validated_secret_id = CreateSecretVersionUseCase._validate_secret_id(secret_id)

        async with self._unit_of_work as unit_of_work:
            secret = await unit_of_work.secrets.get(validated_secret_id)
            if secret is None:
                raise SecretNotFoundError("Secret not found.")

            active_version = await unit_of_work.secret_versions.get_active(validated_secret_id)
            if active_version is None:
                raise SecretVersionNotFoundError("Active secret version not found.")

        return SecretVersionResponse.from_domain(active_version)

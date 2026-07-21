from __future__ import annotations

from collections.abc import Sequence

from application.crypto.use_cases import DecryptSecretValueUseCase, EncryptSecretValueUseCase
from application.secret_version.dto import CreateSecretVersionRequest, SecretVersionResponse
from application.secret_version.exceptions import (
    SecretNotFoundError,
    SecretVersionConflictError,
    SecretVersionCryptoError,
    SecretVersionNotFoundError,
    SecretVersionValidationError,
)
from application.unit_of_work import UnitOfWork
from domain.crypto.entities import SecretEncryptionContext
from domain.crypto.exceptions import CryptoProviderError
from domain.secret.value_objects import SecretId
from domain.secret_version.entities import SecretVersion
from domain.secret_version.exceptions import SecretVersionDomainError
from domain.secret_version.repositories import SecretVersionRepositoryConflictError
from domain.secret_version.value_objects import SecretValue, SecretVersionNumber


class CreateSecretVersionUseCase:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        encrypt_secret_value_use_case: EncryptSecretValueUseCase,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._encrypt_secret_value_use_case = encrypt_secret_value_use_case

    async def execute(self, request: CreateSecretVersionRequest) -> SecretVersionResponse:
        secret_id = self._validate_secret_id(request.secret_id)
        value = self._validate_value(request.value)

        async with self._unit_of_work as unit_of_work:
            secret = await unit_of_work.secrets.get(secret_id)
            if secret is None:
                raise SecretNotFoundError("Secret not found.")

            versions = await unit_of_work.secret_versions.list_versions(secret_id)
            next_version = self._next_version_number(versions)
            encryption_context = SecretEncryptionContext(
                secret_id=str(secret_id),
                version=next_version.value,
            )
            try:
                encrypted_value = self._encrypt_secret_value_use_case.execute(
                    value,
                    encryption_context,
                )
            except CryptoProviderError as exc:
                raise SecretVersionCryptoError("Secret value encryption failed.") from exc

            secret_version = SecretVersion.create(
                secret_id=secret_id,
                encrypted_payload=encrypted_value,
                version=next_version,
            )

            try:
                await unit_of_work.secret_versions.deactivate_previous_versions(secret_id)
                created_secret_version = await unit_of_work.secret_versions.create(secret_version)
            except SecretVersionRepositoryConflictError as exc:
                raise SecretVersionConflictError("Secret version persistence conflict.") from exc

            await unit_of_work.commit()

        return SecretVersionResponse.from_domain(created_secret_version, value)

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
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        decrypt_secret_value_use_case: DecryptSecretValueUseCase,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._decrypt_secret_value_use_case = decrypt_secret_value_use_case

    async def execute(self, secret_id: str) -> tuple[SecretVersionResponse, ...]:
        validated_secret_id = CreateSecretVersionUseCase._validate_secret_id(secret_id)

        async with self._unit_of_work as unit_of_work:
            secret = await unit_of_work.secrets.get(validated_secret_id)
            if secret is None:
                raise SecretNotFoundError("Secret not found.")

            versions = await unit_of_work.secret_versions.list_versions(validated_secret_id)

        return tuple(self._to_response(version) for version in versions)

    def _to_response(self, secret_version: SecretVersion) -> SecretVersionResponse:
        try:
            value = self._decrypt_secret_value_use_case.execute(secret_version)
        except CryptoProviderError as exc:
            raise SecretVersionCryptoError("Secret value decryption failed.") from exc

        return SecretVersionResponse.from_domain(secret_version, value)


class GetActiveSecretVersionUseCase:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        decrypt_secret_value_use_case: DecryptSecretValueUseCase,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._decrypt_secret_value_use_case = decrypt_secret_value_use_case

    async def execute(self, secret_id: str) -> SecretVersionResponse:
        validated_secret_id = CreateSecretVersionUseCase._validate_secret_id(secret_id)

        async with self._unit_of_work as unit_of_work:
            secret = await unit_of_work.secrets.get(validated_secret_id)
            if secret is None:
                raise SecretNotFoundError("Secret not found.")

            active_version = await unit_of_work.secret_versions.get_active(validated_secret_id)
            if active_version is None:
                raise SecretVersionNotFoundError("Active secret version not found.")

        try:
            value = self._decrypt_secret_value_use_case.execute(active_version)
        except CryptoProviderError as exc:
            raise SecretVersionCryptoError("Secret value decryption failed.") from exc

        return SecretVersionResponse.from_domain(active_version, value)

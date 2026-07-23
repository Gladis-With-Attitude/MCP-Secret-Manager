from __future__ import annotations

import logging
from collections.abc import Sequence

from application.audit.dto import AuditContext
from application.audit.use_cases import NoopAuditRecorder, record_audit_event
from application.crypto.use_cases import DecryptSecretValueUseCase, EncryptSecretValueUseCase
from application.observability import log_application_event
from application.secret_version.dto import (
    CreateSecretVersionRequest,
    SecretVersionMetadataResponse,
    SecretVersionResponse,
)
from application.secret_version.exceptions import (
    SecretNotFoundError,
    SecretVersionConflictError,
    SecretVersionCryptoError,
    SecretVersionNotFoundError,
    SecretVersionValidationError,
)
from application.unit_of_work import UnitOfWork
from domain.audit.repositories import AuditRecorder
from domain.audit.value_objects import AuditResult
from domain.crypto.entities import SecretEncryptionContext
from domain.crypto.exceptions import CryptoProviderError
from domain.project.value_objects import ProjectId
from domain.secret.entities import Secret
from domain.secret.value_objects import SecretId
from domain.secret_version.entities import SecretVersion
from domain.secret_version.exceptions import SecretVersionDomainError
from domain.secret_version.repositories import SecretVersionRepositoryConflictError
from domain.secret_version.value_objects import SecretValue, SecretVersionNumber

logger = logging.getLogger(__name__)


class CreateSecretVersionUseCase:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        encrypt_secret_value_use_case: EncryptSecretValueUseCase,
        audit_recorder: AuditRecorder | None = None,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._encrypt_secret_value_use_case = encrypt_secret_value_use_case
        self._audit_recorder = audit_recorder or NoopAuditRecorder()

    async def execute(self, request: CreateSecretVersionRequest) -> SecretVersionMetadataResponse:
        try:
            secret_id = self._validate_secret_id(request.secret_id)
            value = self._validate_value(request.value)

            async with self._unit_of_work as unit_of_work:
                secret = await unit_of_work.secrets.get(secret_id)
                if secret is None:
                    raise SecretNotFoundError("Secret not found.")
                self._ensure_secret_belongs_to_project(secret, request.project_id)

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
                    created_secret_version = await unit_of_work.secret_versions.create(
                        secret_version
                    )
                except SecretVersionRepositoryConflictError as exc:
                    raise SecretVersionConflictError(
                        "Secret version persistence conflict."
                    ) from exc

                await unit_of_work.commit()
        except Exception:
            log_application_event(
                logger,
                event="secret_version_create",
                result=AuditResult.FAILURE,
                resource_id=request.secret_id,
                project_id=request.project_id,
            )
            await record_audit_event(
                self._audit_recorder,
                request.audit_context,
                action="secret.rotate",
                resource_type="secret",
                resource_id=request.secret_id,
                result=AuditResult.FAILURE,
            )
            raise

        log_application_event(
            logger,
            event="secret_version_create",
            result=AuditResult.SUCCESS,
            resource_id=str(created_secret_version.secret_id),
            version_id=str(created_secret_version.id),
            version=created_secret_version.version.value,
            active=created_secret_version.active,
        )
        await record_audit_event(
            self._audit_recorder,
            request.audit_context,
            action="secret.rotate",
            resource_type="secret",
            resource_id=str(created_secret_version.secret_id),
            result=AuditResult.SUCCESS,
            metadata={"version": created_secret_version.version.value},
        )

        return SecretVersionMetadataResponse.from_domain(created_secret_version)

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

    @staticmethod
    def _validate_project_id(raw_project_id: str) -> ProjectId:
        try:
            return ProjectId.from_string(raw_project_id)
        except ValueError as exc:
            raise SecretVersionValidationError("Project id must be a valid UUID.") from exc

    @staticmethod
    def _ensure_secret_belongs_to_project(secret: Secret, raw_project_id: str | None) -> None:
        if raw_project_id is None:
            return
        project_id = CreateSecretVersionUseCase._validate_project_id(raw_project_id)
        if secret.project_id != project_id:
            raise SecretNotFoundError("Secret not found.")


class ListSecretVersionsUseCase:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        audit_recorder: AuditRecorder | None = None,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._audit_recorder = audit_recorder or NoopAuditRecorder()

    async def execute(
        self,
        secret_id: str,
        audit_context: AuditContext | None = None,
        project_id: str | None = None,
    ) -> tuple[SecretVersionMetadataResponse, ...]:
        try:
            validated_secret_id = CreateSecretVersionUseCase._validate_secret_id(secret_id)

            async with self._unit_of_work as unit_of_work:
                secret = await unit_of_work.secrets.get(validated_secret_id)
                if secret is None:
                    raise SecretNotFoundError("Secret not found.")
                CreateSecretVersionUseCase._ensure_secret_belongs_to_project(secret, project_id)

                versions = await unit_of_work.secret_versions.list_versions(validated_secret_id)

            response = tuple(
                SecretVersionMetadataResponse.from_domain(version) for version in versions
            )
        except Exception:
            log_application_event(
                logger,
                event="secret_version_list",
                result=AuditResult.FAILURE,
                resource_id=secret_id,
                project_id=project_id,
            )
            await record_audit_event(
                self._audit_recorder,
                audit_context,
                action="secret.read",
                resource_type="secret",
                resource_id=secret_id,
                result=AuditResult.FAILURE,
            )
            raise

        log_application_event(
            logger,
            event="secret_version_list",
            result=AuditResult.SUCCESS,
            resource_id=str(validated_secret_id),
            returned_count=len(response),
        )
        await record_audit_event(
            self._audit_recorder,
            audit_context,
            action="secret.read",
            resource_type="secret",
            resource_id=str(validated_secret_id),
            result=AuditResult.SUCCESS,
            metadata={"versions_returned": len(response)},
        )
        return response


class GetActiveSecretVersionUseCase:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        decrypt_secret_value_use_case: DecryptSecretValueUseCase,
        audit_recorder: AuditRecorder | None = None,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._decrypt_secret_value_use_case = decrypt_secret_value_use_case
        self._audit_recorder = audit_recorder or NoopAuditRecorder()

    async def execute(
        self,
        secret_id: str,
        audit_context: AuditContext | None = None,
        project_id: str | None = None,
    ) -> SecretVersionResponse:
        try:
            validated_secret_id = CreateSecretVersionUseCase._validate_secret_id(secret_id)

            async with self._unit_of_work as unit_of_work:
                secret = await unit_of_work.secrets.get(validated_secret_id)
                if secret is None:
                    raise SecretNotFoundError("Secret not found.")
                CreateSecretVersionUseCase._ensure_secret_belongs_to_project(secret, project_id)

                active_version = await unit_of_work.secret_versions.get_active(validated_secret_id)
                if active_version is None:
                    raise SecretVersionNotFoundError("Active secret version not found.")

            try:
                value = self._decrypt_secret_value_use_case.execute(active_version)
            except CryptoProviderError as exc:
                raise SecretVersionCryptoError("Secret value decryption failed.") from exc
        except Exception:
            log_application_event(
                logger,
                event="secret_version_decrypt",
                result=AuditResult.FAILURE,
                resource_id=secret_id,
                project_id=project_id,
            )
            await record_audit_event(
                self._audit_recorder,
                audit_context,
                action="secret.decrypt",
                resource_type="secret",
                resource_id=secret_id,
                result=AuditResult.FAILURE,
            )
            raise

        log_application_event(
            logger,
            event="secret_version_decrypt",
            result=AuditResult.SUCCESS,
            resource_id=str(validated_secret_id),
            version_id=str(active_version.id),
            version=active_version.version.value,
        )
        await record_audit_event(
            self._audit_recorder,
            audit_context,
            action="secret.decrypt",
            resource_type="secret",
            resource_id=str(validated_secret_id),
            result=AuditResult.SUCCESS,
            metadata={"version": active_version.version.value},
        )

        return SecretVersionResponse.from_domain(active_version, value)

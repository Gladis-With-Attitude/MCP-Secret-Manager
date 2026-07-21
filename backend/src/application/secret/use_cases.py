from __future__ import annotations

from application.audit.use_cases import NoopAuditRecorder, record_audit_event
from application.secret.dto import (
    CreateSecretRequest,
    GetSecretRequest,
    ListSecretsRequest,
    SearchSecretsRequest,
    SecretResponse,
)
from application.secret.exceptions import (
    ProjectNotFoundError,
    SecretAlreadyExistsError,
    SecretNotFoundError,
    SecretValidationError,
)
from application.unit_of_work import UnitOfWork
from domain.audit.repositories import AuditRecorder
from domain.audit.value_objects import AuditResult
from domain.project.value_objects import ProjectId
from domain.secret.entities import Secret
from domain.secret.exceptions import SecretDomainError
from domain.secret.repositories import SecretRepositoryConflictError
from domain.secret.value_objects import SecretDescription, SecretId, SecretKey


class CreateSecretUseCase:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        audit_recorder: AuditRecorder | None = None,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._audit_recorder = audit_recorder or NoopAuditRecorder()

    async def execute(self, request: CreateSecretRequest) -> SecretResponse:
        try:
            project_id = self._validate_project_id(request.project_id)
            key = self._validate_key(request.key)
            description = SecretDescription(request.description)

            async with self._unit_of_work as unit_of_work:
                project = await unit_of_work.projects.get(project_id)
                if project is None:
                    raise ProjectNotFoundError("Project not found.")

                if await unit_of_work.secrets.exists_in_project(project_id, key):
                    raise SecretAlreadyExistsError(
                        "A secret with this key already exists in this project."
                    )

                secret = Secret.create(project_id=project_id, key=key, description=description)

                try:
                    created_secret = await unit_of_work.secrets.create(secret)
                except SecretRepositoryConflictError as exc:
                    raise SecretAlreadyExistsError(
                        "A secret with this key already exists in this project."
                    ) from exc

                await unit_of_work.commit()
        except Exception:
            await record_audit_event(
                self._audit_recorder,
                request.audit_context,
                action="secret.create",
                resource_type="secret",
                resource_id=None,
                result=AuditResult.FAILURE,
                metadata={"project_id": request.project_id, "key": request.key},
            )
            raise

        await record_audit_event(
            self._audit_recorder,
            request.audit_context,
            action="secret.create",
            resource_type="secret",
            resource_id=str(created_secret.id),
            result=AuditResult.SUCCESS,
            metadata={
                "project_id": str(created_secret.project_id),
                "key": created_secret.key.value,
            },
        )

        return SecretResponse.from_domain(created_secret)

    @staticmethod
    def _validate_project_id(raw_project_id: str) -> ProjectId:
        try:
            return ProjectId.from_string(raw_project_id)
        except ValueError as exc:
            raise SecretValidationError("Project id must be a valid UUID.") from exc

    @staticmethod
    def _validate_key(raw_key: str) -> SecretKey:
        try:
            return SecretKey(raw_key)
        except SecretDomainError as exc:
            raise SecretValidationError(str(exc)) from exc

    @staticmethod
    def _validate_secret_id(raw_secret_id: str) -> SecretId:
        try:
            return SecretId.from_string(raw_secret_id)
        except ValueError as exc:
            raise SecretValidationError("Secret id must be a valid UUID.") from exc


class ListSecretsUseCase:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        audit_recorder: AuditRecorder | None = None,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._audit_recorder = audit_recorder or NoopAuditRecorder()

    async def execute(self, request: ListSecretsRequest) -> tuple[SecretResponse, ...]:
        try:
            project_id = CreateSecretUseCase._validate_project_id(request.project_id)
            async with self._unit_of_work as unit_of_work:
                project = await unit_of_work.projects.get(project_id)
                if project is None:
                    raise ProjectNotFoundError("Project not found.")
                secrets = await unit_of_work.secrets.list_by_project(project_id)
        except Exception:
            await record_audit_event(
                self._audit_recorder,
                request.audit_context,
                action="secret.read",
                resource_type="project",
                resource_id=request.project_id,
                result=AuditResult.FAILURE,
            )
            raise

        await record_audit_event(
            self._audit_recorder,
            request.audit_context,
            action="secret.read",
            resource_type="project",
            resource_id=str(project_id),
            result=AuditResult.SUCCESS,
            metadata={"count": len(secrets)},
        )
        return tuple(SecretResponse.from_domain(secret) for secret in secrets)


class GetSecretUseCase:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        audit_recorder: AuditRecorder | None = None,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._audit_recorder = audit_recorder or NoopAuditRecorder()

    async def execute(self, request: GetSecretRequest) -> SecretResponse:
        try:
            project_id = CreateSecretUseCase._validate_project_id(request.project_id)
            secret_id = CreateSecretUseCase._validate_secret_id(request.secret_id)
            async with self._unit_of_work as unit_of_work:
                secret = await unit_of_work.secrets.get(secret_id)
                if secret is None or secret.project_id != project_id:
                    raise SecretNotFoundError("Secret not found.")
        except Exception:
            await record_audit_event(
                self._audit_recorder,
                request.audit_context,
                action="secret.read",
                resource_type="secret",
                resource_id=request.secret_id,
                result=AuditResult.FAILURE,
                metadata={"project_id": request.project_id},
            )
            raise

        await record_audit_event(
            self._audit_recorder,
            request.audit_context,
            action="secret.read",
            resource_type="secret",
            resource_id=str(secret.id),
            result=AuditResult.SUCCESS,
            metadata={"project_id": str(secret.project_id), "key": secret.key.value},
        )
        return SecretResponse.from_domain(secret)


class SearchSecretsUseCase:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        audit_recorder: AuditRecorder | None = None,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._audit_recorder = audit_recorder or NoopAuditRecorder()

    async def execute(self, request: SearchSecretsRequest) -> tuple[SecretResponse, ...]:
        query = request.query.strip().upper()
        try:
            project_id = CreateSecretUseCase._validate_project_id(request.project_id)
            async with self._unit_of_work as unit_of_work:
                project = await unit_of_work.projects.get(project_id)
                if project is None:
                    raise ProjectNotFoundError("Project not found.")
                secrets = await unit_of_work.secrets.list_by_project(project_id)
            matching = tuple(secret for secret in secrets if query in secret.key.value)
        except Exception:
            await record_audit_event(
                self._audit_recorder,
                request.audit_context,
                action="secret.read",
                resource_type="project",
                resource_id=request.project_id,
                result=AuditResult.FAILURE,
                metadata={"query": request.query},
            )
            raise

        await record_audit_event(
            self._audit_recorder,
            request.audit_context,
            action="secret.read",
            resource_type="project",
            resource_id=str(project_id),
            result=AuditResult.SUCCESS,
            metadata={"query": query, "count": len(matching)},
        )
        return tuple(SecretResponse.from_domain(secret) for secret in matching)

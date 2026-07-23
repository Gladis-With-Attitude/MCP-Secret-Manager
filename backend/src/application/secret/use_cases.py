from __future__ import annotations

import logging

from application.audit.use_cases import NoopAuditRecorder, record_audit_event
from application.observability import log_application_event
from application.secret.dto import (
    ArchiveSecretRequest,
    CreateSecretRequest,
    GetSecretRequest,
    ListSecretsRequest,
    PaginationResponse,
    SearchSecretsRequest,
    SecretListResponse,
    SecretPermissionsResponse,
    SecretResponse,
    UpdateSecretRequest,
)
from application.secret.exceptions import (
    ProjectArchivedError,
    ProjectNotFoundError,
    SecretAlreadyExistsError,
    SecretArchivedError,
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
from domain.secret.value_objects import (
    SecretDescription,
    SecretId,
    SecretKey,
    SecretMetadata,
    SecretMetadataObject,
    SecretTags,
    SecretType,
)

logger = logging.getLogger(__name__)


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
            description = self._validate_description(request.description)
            secret_type = self._validate_type(request.type)
            metadata = self._validate_metadata(request.metadata)
            tags = self._validate_tags(request.tags)

            async with self._unit_of_work as unit_of_work:
                project = await unit_of_work.projects.get(project_id)
                if project is None:
                    raise ProjectNotFoundError("Project not found.")
                if project.archived:
                    raise ProjectArchivedError("Archived projects cannot receive new secrets.")

                if await unit_of_work.secrets.exists_in_project(project_id, key):
                    raise SecretAlreadyExistsError(
                        "A secret with this key already exists in this project."
                    )

                secret = Secret.create(
                    project_id=project_id,
                    key=key,
                    description=description,
                    secret_type=secret_type,
                    metadata=metadata,
                    tags=tags,
                )

                try:
                    created_secret = await unit_of_work.secrets.create(secret)
                except SecretRepositoryConflictError as exc:
                    raise SecretAlreadyExistsError(
                        "A secret with this key already exists in this project."
                    ) from exc

                await unit_of_work.commit()
        except Exception:
            log_application_event(
                logger,
                event="secret_create",
                result=AuditResult.FAILURE,
                project_id=request.project_id,
            )
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

        log_application_event(
            logger,
            event="secret_create",
            result=AuditResult.SUCCESS,
            resource_id=str(created_secret.id),
            project_id=str(created_secret.project_id),
            category=created_secret.type.value,
            tags_count=len(created_secret.tags.value),
            metadata_keys_count=len(created_secret.metadata.value),
        )
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

    @staticmethod
    def _validate_description(raw_description: str | None) -> SecretDescription:
        try:
            return SecretDescription(raw_description)
        except SecretDomainError as exc:
            raise SecretValidationError(str(exc)) from exc

    @staticmethod
    def _validate_type(raw_type: str | None) -> SecretType:
        try:
            return SecretType(raw_type or "generic")
        except SecretDomainError as exc:
            raise SecretValidationError(str(exc)) from exc

    @staticmethod
    def _validate_tags(raw_tags: tuple[str, ...]) -> SecretTags:
        try:
            return SecretTags(raw_tags)
        except SecretDomainError as exc:
            raise SecretValidationError(str(exc)) from exc

    @staticmethod
    def _validate_metadata(raw_metadata: SecretMetadata | None) -> SecretMetadataObject:
        try:
            return SecretMetadataObject(raw_metadata or {})
        except SecretDomainError as exc:
            raise SecretValidationError(str(exc)) from exc


class ListSecretsUseCase:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        audit_recorder: AuditRecorder | None = None,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._audit_recorder = audit_recorder or NoopAuditRecorder()

    async def execute(self, request: ListSecretsRequest) -> SecretListResponse:
        try:
            project_id = CreateSecretUseCase._validate_project_id(request.project_id)
            page = self._validate_page(request.page)
            page_size = self._validate_page_size(request.page_size)
            status = self._validate_status(request.status)
            secret_type = self._validate_type_filter(request.type)
            include_archived = bool(request.archived) or status == "archived"
            offset = (page - 1) * page_size

            async with self._unit_of_work as unit_of_work:
                project = await unit_of_work.projects.get(project_id)
                if project is None:
                    raise ProjectNotFoundError("Project not found.")
                total = await unit_of_work.secrets.count_by_project(
                    project_id,
                    include_archived=include_archived,
                    search=request.search,
                    status=status,
                    secret_type=secret_type,
                )
                secrets = await unit_of_work.secrets.list_by_project(
                    project_id,
                    include_archived=include_archived,
                    limit=page_size,
                    offset=offset,
                    search=request.search,
                    status=status,
                    secret_type=secret_type,
                )
        except Exception:
            log_application_event(
                logger,
                event="secret_list",
                result=AuditResult.FAILURE,
                project_id=request.project_id,
            )
            await record_audit_event(
                self._audit_recorder,
                request.audit_context,
                action="secret.read",
                resource_type="project",
                resource_id=request.project_id,
                result=AuditResult.FAILURE,
            )
            raise

        log_application_event(
            logger,
            event="secret_list",
            result=AuditResult.SUCCESS,
            project_id=str(project_id),
            returned_count=len(secrets),
            total_count=total,
            page=page,
            page_size=page_size,
            include_archived=include_archived,
            status_filter_configured=status is not None,
            type_filter_configured=secret_type is not None,
            search_configured=bool(request.search),
        )
        await record_audit_event(
            self._audit_recorder,
            request.audit_context,
            action="secret.read",
            resource_type="project",
            resource_id=str(project_id),
            result=AuditResult.SUCCESS,
            metadata={"count": len(secrets)},
        )
        return SecretListResponse(
            data=tuple(SecretResponse.from_domain(secret) for secret in secrets),
            pagination=PaginationResponse(
                page=page,
                page_size=page_size,
                total=total,
                has_next_page=offset + page_size < total,
                has_previous_page=page > 1,
            ),
            permissions=SecretPermissionsResponse(
                create=True,
                read=True,
                update=True,
                archive=True,
                delete=False,
                read_value=False,
            ),
        )

    @staticmethod
    def _validate_page(raw_page: int) -> int:
        if raw_page < 1:
            raise SecretValidationError("Page must be greater than or equal to 1.")
        return raw_page

    @staticmethod
    def _validate_page_size(raw_page_size: int) -> int:
        if raw_page_size < 1 or raw_page_size > 100:
            raise SecretValidationError("Page size must be between 1 and 100.")
        return raw_page_size

    @staticmethod
    def _validate_status(raw_status: str | None) -> str | None:
        if raw_status is None:
            return None
        normalized_status = raw_status.strip().lower()
        if normalized_status in {"active", "archived"}:
            return normalized_status
        raise SecretValidationError("Secret status filter is invalid.")

    @staticmethod
    def _validate_type_filter(raw_type: str | None) -> str | None:
        if raw_type is None:
            return None
        return CreateSecretUseCase._validate_type(raw_type).value


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
            secret_id = CreateSecretUseCase._validate_secret_id(request.secret_id)
            project_id = (
                CreateSecretUseCase._validate_project_id(request.project_id)
                if request.project_id is not None
                else None
            )
            async with self._unit_of_work as unit_of_work:
                secret = await unit_of_work.secrets.get(secret_id)
                if secret is None or (project_id is not None and secret.project_id != project_id):
                    raise SecretNotFoundError("Secret not found.")
        except Exception:
            log_application_event(
                logger,
                event="secret_get",
                result=AuditResult.FAILURE,
                resource_id=request.secret_id,
                project_id=request.project_id,
            )
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

        log_application_event(
            logger,
            event="secret_get",
            result=AuditResult.SUCCESS,
            resource_id=str(secret.id),
            project_id=str(secret.project_id),
            archived=secret.archived,
        )
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
                secrets = await unit_of_work.secrets.list_by_project(
                    project_id,
                    include_archived=True,
                    search=query,
                    secret_type=None,
                )
            matching = tuple(secret for secret in secrets if query in secret.key.value)
        except Exception:
            log_application_event(
                logger,
                event="secret_search",
                result=AuditResult.FAILURE,
                project_id=request.project_id,
                query_configured=bool(request.query.strip()),
            )
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

        log_application_event(
            logger,
            event="secret_search",
            result=AuditResult.SUCCESS,
            project_id=str(project_id),
            returned_count=len(matching),
            query_configured=bool(query),
        )
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


class UpdateSecretUseCase:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        audit_recorder: AuditRecorder | None = None,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._audit_recorder = audit_recorder or NoopAuditRecorder()

    async def execute(self, request: UpdateSecretRequest) -> SecretResponse:
        try:
            secret_id = CreateSecretUseCase._validate_secret_id(request.secret_id)
            key = CreateSecretUseCase._validate_key(request.key)
            description = CreateSecretUseCase._validate_description(request.description)
            secret_type = CreateSecretUseCase._validate_type(request.type)
            metadata = CreateSecretUseCase._validate_metadata(request.metadata)
            tags = CreateSecretUseCase._validate_tags(request.tags)

            async with self._unit_of_work as unit_of_work:
                secret = await unit_of_work.secrets.get(secret_id)
                if secret is None:
                    raise SecretNotFoundError("Secret not found.")
                if secret.archived:
                    raise SecretArchivedError("Archived secrets cannot be updated.")
                if await unit_of_work.secrets.exists_in_project(
                    secret.project_id,
                    key,
                    exclude_secret_id=secret_id,
                ):
                    raise SecretAlreadyExistsError(
                        "A secret with this key already exists in this project."
                    )

                try:
                    updated_secret = await unit_of_work.secrets.update(
                        secret.update_metadata(
                            key=key,
                            description=description,
                            secret_type=secret_type,
                            metadata=metadata,
                            tags=tags,
                        )
                    )
                except SecretRepositoryConflictError as exc:
                    raise SecretAlreadyExistsError(
                        "A secret with this key already exists in this project."
                    ) from exc

                await unit_of_work.commit()
        except Exception:
            log_application_event(
                logger,
                event="secret_update",
                result=AuditResult.FAILURE,
                resource_id=request.secret_id,
            )
            await record_audit_event(
                self._audit_recorder,
                request.audit_context,
                action="secret.update",
                resource_type="secret",
                resource_id=request.secret_id,
                result=AuditResult.FAILURE,
                metadata={"key": request.key},
            )
            raise

        log_application_event(
            logger,
            event="secret_update",
            result=AuditResult.SUCCESS,
            resource_id=str(updated_secret.id),
            project_id=str(updated_secret.project_id),
            category=updated_secret.type.value,
            tags_count=len(updated_secret.tags.value),
            metadata_keys_count=len(updated_secret.metadata.value),
        )
        await record_audit_event(
            self._audit_recorder,
            request.audit_context,
            action="secret.update",
            resource_type="secret",
            resource_id=str(updated_secret.id),
            result=AuditResult.SUCCESS,
            metadata={
                "project_id": str(updated_secret.project_id),
                "key": updated_secret.key.value,
            },
        )
        return SecretResponse.from_domain(updated_secret)


class ArchiveSecretUseCase:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        audit_recorder: AuditRecorder | None = None,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._audit_recorder = audit_recorder or NoopAuditRecorder()

    async def execute(self, request: ArchiveSecretRequest) -> SecretResponse:
        try:
            secret_id = CreateSecretUseCase._validate_secret_id(request.secret_id)
            async with self._unit_of_work as unit_of_work:
                secret = await unit_of_work.secrets.get(secret_id)
                if secret is None:
                    raise SecretNotFoundError("Secret not found.")

                archived_secret = secret
                if not secret.archived:
                    archived_secret = await unit_of_work.secrets.update(secret.archive())
                await unit_of_work.commit()
        except Exception:
            log_application_event(
                logger,
                event="secret_archive",
                result=AuditResult.FAILURE,
                resource_id=request.secret_id,
            )
            await record_audit_event(
                self._audit_recorder,
                request.audit_context,
                action="secret.archive",
                resource_type="secret",
                resource_id=request.secret_id,
                result=AuditResult.FAILURE,
            )
            raise

        log_application_event(
            logger,
            event="secret_archive",
            result=AuditResult.SUCCESS,
            resource_id=str(archived_secret.id),
            project_id=str(archived_secret.project_id),
            archived=archived_secret.archived,
        )
        await record_audit_event(
            self._audit_recorder,
            request.audit_context,
            action="secret.archive",
            resource_type="secret",
            resource_id=str(archived_secret.id),
            result=AuditResult.SUCCESS,
            metadata={
                "project_id": str(archived_secret.project_id),
            },
        )
        return SecretResponse.from_domain(archived_secret)

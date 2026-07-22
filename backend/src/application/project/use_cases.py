from __future__ import annotations

from application.audit.use_cases import NoopAuditRecorder, record_audit_event
from application.project.dto import (
    ArchiveProjectRequest,
    CreateProjectRequest,
    GetProjectRequest,
    ListProjectsRequest,
    PaginationResponse,
    ProjectListResponse,
    ProjectPermissionsResponse,
    ProjectResponse,
    UpdateProjectRequest,
)
from application.project.exceptions import (
    ProjectAlreadyExistsError,
    ProjectArchivedError,
    ProjectNotFoundError,
    ProjectValidationError,
    VaultNotFoundError,
)
from application.unit_of_work import UnitOfWork
from domain.audit.repositories import AuditRecorder
from domain.audit.value_objects import AuditResult
from domain.project.entities import Project
from domain.project.exceptions import ProjectDomainError
from domain.project.repositories import ProjectRepositoryConflictError
from domain.project.value_objects import ProjectDescription, ProjectId, ProjectName
from domain.vault.value_objects import VaultId


class CreateProjectUseCase:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        audit_recorder: AuditRecorder | None = None,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._audit_recorder = audit_recorder or NoopAuditRecorder()

    async def execute(self, request: CreateProjectRequest) -> ProjectResponse:
        try:
            vault_id = self._validate_vault_id(request.vault_id)
            name = self._validate_name(request.name)
            description = self._validate_description(request.description)

            async with self._unit_of_work as unit_of_work:
                vault = await unit_of_work.vaults.get(vault_id)
                if vault is None:
                    raise VaultNotFoundError("Vault not found.")

                if await unit_of_work.projects.exists_in_vault(vault_id, name):
                    raise ProjectAlreadyExistsError(
                        "A project with this name already exists in this vault."
                    )

                project = Project.create(
                    vault_id=vault_id,
                    name=name,
                    description=description,
                )

                try:
                    created_project = await unit_of_work.projects.create(project)
                except ProjectRepositoryConflictError as exc:
                    raise ProjectAlreadyExistsError(
                        "A project with this name already exists in this vault."
                    ) from exc

                await unit_of_work.commit()
        except Exception:
            await record_audit_event(
                self._audit_recorder,
                request.audit_context,
                action="project.create",
                resource_type="project",
                resource_id=None,
                result=AuditResult.FAILURE,
                metadata={"vault_id": request.vault_id, "name": request.name},
            )
            raise

        await record_audit_event(
            self._audit_recorder,
            request.audit_context,
            action="project.create",
            resource_type="project",
            resource_id=str(created_project.id),
            result=AuditResult.SUCCESS,
            metadata={
                "vault_id": str(created_project.vault_id),
                "name": created_project.name.value,
            },
        )

        return ProjectResponse.from_domain(created_project)

    @staticmethod
    def _validate_vault_id(raw_vault_id: str) -> VaultId:
        try:
            return VaultId.from_string(raw_vault_id)
        except ValueError as exc:
            raise ProjectValidationError("Vault id must be a valid UUID.") from exc

    @staticmethod
    def _validate_name(raw_name: str) -> ProjectName:
        try:
            return ProjectName(raw_name)
        except ProjectDomainError as exc:
            raise ProjectValidationError(str(exc)) from exc

    @staticmethod
    def _validate_description(raw_description: str | None) -> ProjectDescription:
        try:
            return ProjectDescription(raw_description)
        except ProjectDomainError as exc:
            raise ProjectValidationError(str(exc)) from exc

    @staticmethod
    def _validate_project_id(raw_project_id: str) -> ProjectId:
        try:
            return ProjectId.from_string(raw_project_id)
        except ValueError as exc:
            raise ProjectValidationError("Project id must be a valid UUID.") from exc


class ListProjectsUseCase:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def execute(self, request: ListProjectsRequest | str) -> ProjectListResponse:
        filters = (
            request if isinstance(request, ListProjectsRequest) else ListProjectsRequest(request)
        )
        validated_vault_id = CreateProjectUseCase._validate_vault_id(filters.vault_id)
        page = self._validate_page(filters.page)
        page_size = self._validate_page_size(filters.page_size)
        status = self._validate_status(filters.status)
        include_archived = bool(filters.archived) or status == "archived"
        offset = (page - 1) * page_size

        async with self._unit_of_work as unit_of_work:
            vault = await unit_of_work.vaults.get(validated_vault_id)
            if vault is None:
                raise VaultNotFoundError("Vault not found.")
            total = await unit_of_work.projects.count_by_vault(
                validated_vault_id,
                include_archived=include_archived,
                search=filters.search,
                status=status,
            )
            projects = await unit_of_work.projects.list_by_vault(
                validated_vault_id,
                include_archived=include_archived,
                limit=page_size,
                offset=offset,
                search=filters.search,
                status=status,
            )

        return ProjectListResponse(
            data=tuple(ProjectResponse.from_domain(project) for project in projects),
            pagination=PaginationResponse(
                page=page,
                page_size=page_size,
                total=total,
                has_next_page=offset + page_size < total,
                has_previous_page=page > 1,
            ),
            permissions=ProjectPermissionsResponse(
                create=True,
                read=True,
                update=True,
                archive=True,
                delete=False,
            ),
        )

    @staticmethod
    def _validate_page(raw_page: int) -> int:
        if raw_page < 1:
            raise ProjectValidationError("Page must be greater than or equal to 1.")
        return raw_page

    @staticmethod
    def _validate_page_size(raw_page_size: int) -> int:
        if raw_page_size < 1 or raw_page_size > 100:
            raise ProjectValidationError("Page size must be between 1 and 100.")
        return raw_page_size

    @staticmethod
    def _validate_status(raw_status: str | None) -> str | None:
        if raw_status is None:
            return None
        normalized_status = raw_status.strip().lower()
        if normalized_status in {"active", "archived"}:
            return normalized_status
        raise ProjectValidationError("Project status filter is invalid.")


class GetProjectUseCase:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        audit_recorder: AuditRecorder | None = None,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._audit_recorder = audit_recorder or NoopAuditRecorder()

    async def execute(self, request: GetProjectRequest) -> ProjectResponse:
        try:
            project_id = CreateProjectUseCase._validate_project_id(request.project_id)
            async with self._unit_of_work as unit_of_work:
                project = await unit_of_work.projects.get(project_id)
                if project is None:
                    raise ProjectNotFoundError("Project not found.")
        except Exception:
            await record_audit_event(
                self._audit_recorder,
                request.audit_context,
                action="project.read",
                resource_type="project",
                resource_id=request.project_id,
                result=AuditResult.FAILURE,
                metadata={},
            )
            raise

        await record_audit_event(
            self._audit_recorder,
            request.audit_context,
            action="project.read",
            resource_type="project",
            resource_id=str(project.id),
            result=AuditResult.SUCCESS,
            metadata={},
        )

        return ProjectResponse.from_domain(project)


class UpdateProjectUseCase:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        audit_recorder: AuditRecorder | None = None,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._audit_recorder = audit_recorder or NoopAuditRecorder()

    async def execute(self, request: UpdateProjectRequest) -> ProjectResponse:
        try:
            project_id = CreateProjectUseCase._validate_project_id(request.project_id)
            name = CreateProjectUseCase._validate_name(request.name)
            description = CreateProjectUseCase._validate_description(request.description)

            async with self._unit_of_work as unit_of_work:
                project = await unit_of_work.projects.get(project_id)
                if project is None:
                    raise ProjectNotFoundError("Project not found.")
                if project.archived:
                    raise ProjectArchivedError("Archived projects cannot be updated.")
                if await unit_of_work.projects.exists_in_vault(
                    project.vault_id,
                    name,
                    exclude_project_id=project_id,
                ):
                    raise ProjectAlreadyExistsError(
                        "A project with this name already exists in this vault."
                    )

                try:
                    updated_project = await unit_of_work.projects.update(
                        project.update_metadata(name=name, description=description)
                    )
                except ProjectRepositoryConflictError as exc:
                    raise ProjectAlreadyExistsError(
                        "A project with this name already exists in this vault."
                    ) from exc

                await unit_of_work.commit()
        except Exception:
            await record_audit_event(
                self._audit_recorder,
                request.audit_context,
                action="project.update",
                resource_type="project",
                resource_id=request.project_id,
                result=AuditResult.FAILURE,
                metadata={"name": request.name},
            )
            raise

        await record_audit_event(
            self._audit_recorder,
            request.audit_context,
            action="project.update",
            resource_type="project",
            resource_id=str(updated_project.id),
            result=AuditResult.SUCCESS,
            metadata={"name": updated_project.name.value},
        )

        return ProjectResponse.from_domain(updated_project)


class ArchiveProjectUseCase:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        audit_recorder: AuditRecorder | None = None,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._audit_recorder = audit_recorder or NoopAuditRecorder()

    async def execute(self, request: ArchiveProjectRequest) -> ProjectResponse:
        try:
            project_id = CreateProjectUseCase._validate_project_id(request.project_id)
            async with self._unit_of_work as unit_of_work:
                project = await unit_of_work.projects.get(project_id)
                if project is None:
                    raise ProjectNotFoundError("Project not found.")

                archived_project = (
                    project
                    if project.archived
                    else await unit_of_work.projects.update(project.archive())
                )
                await unit_of_work.commit()
        except Exception:
            await record_audit_event(
                self._audit_recorder,
                request.audit_context,
                action="project.archive",
                resource_type="project",
                resource_id=request.project_id,
                result=AuditResult.FAILURE,
                metadata={},
            )
            raise

        await record_audit_event(
            self._audit_recorder,
            request.audit_context,
            action="project.archive",
            resource_type="project",
            resource_id=str(archived_project.id),
            result=AuditResult.SUCCESS,
            metadata={},
        )

        return ProjectResponse.from_domain(archived_project)

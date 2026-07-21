from __future__ import annotations

from application.audit.use_cases import NoopAuditRecorder, record_audit_event
from application.project.dto import CreateProjectRequest, ProjectResponse
from application.project.exceptions import (
    ProjectAlreadyExistsError,
    ProjectValidationError,
    VaultNotFoundError,
)
from application.unit_of_work import UnitOfWork
from domain.audit.repositories import AuditRecorder
from domain.audit.value_objects import AuditResult
from domain.project.entities import Project
from domain.project.exceptions import ProjectDomainError
from domain.project.repositories import ProjectRepositoryConflictError
from domain.project.value_objects import ProjectName
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

            async with self._unit_of_work as unit_of_work:
                vault = await unit_of_work.vaults.get(vault_id)
                if vault is None:
                    raise VaultNotFoundError("Vault not found.")

                if await unit_of_work.projects.exists_in_vault(vault_id, name):
                    raise ProjectAlreadyExistsError(
                        "A project with this name already exists in this vault."
                    )

                project = Project.create(vault_id=vault_id, name=name)

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

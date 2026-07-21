from __future__ import annotations

from application.project.dto import CreateProjectRequest, ProjectResponse
from application.project.exceptions import (
    ProjectAlreadyExistsError,
    ProjectValidationError,
    VaultNotFoundError,
)
from application.unit_of_work import UnitOfWork
from domain.project.entities import Project
from domain.project.exceptions import ProjectDomainError
from domain.project.repositories import ProjectRepositoryConflictError
from domain.project.value_objects import ProjectName
from domain.vault.value_objects import VaultId


class CreateProjectUseCase:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def execute(self, request: CreateProjectRequest) -> ProjectResponse:
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

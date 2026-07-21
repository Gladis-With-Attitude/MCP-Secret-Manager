from __future__ import annotations

from application.secret.dto import CreateSecretRequest, SecretResponse
from application.secret.exceptions import (
    ProjectNotFoundError,
    SecretAlreadyExistsError,
    SecretValidationError,
)
from application.unit_of_work import UnitOfWork
from domain.project.value_objects import ProjectId
from domain.secret.entities import Secret
from domain.secret.exceptions import SecretDomainError
from domain.secret.repositories import SecretRepositoryConflictError
from domain.secret.value_objects import SecretDescription, SecretKey


class CreateSecretUseCase:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def execute(self, request: CreateSecretRequest) -> SecretResponse:
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

from __future__ import annotations

from application.unit_of_work import UnitOfWork
from application.vault.dto import CreateVaultRequest, VaultResponse
from application.vault.exceptions import VaultAlreadyExistsError, VaultValidationError
from domain.vault.entities import Vault
from domain.vault.exceptions import VaultDomainError
from domain.vault.repositories import VaultRepositoryConflictError
from domain.vault.value_objects import VaultName


class CreateVaultUseCase:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def execute(self, request: CreateVaultRequest) -> VaultResponse:
        name = self._validate_name(request.name)

        async with self._unit_of_work as unit_of_work:
            if await unit_of_work.vaults.exists_by_name(name):
                raise VaultAlreadyExistsError("A vault with this name already exists.")

            vault = Vault.create(name=name)

            try:
                created_vault = await unit_of_work.vaults.create(vault)
            except VaultRepositoryConflictError as exc:
                raise VaultAlreadyExistsError("A vault with this name already exists.") from exc

            await unit_of_work.commit()

        return VaultResponse.from_domain(created_vault)

    @staticmethod
    def _validate_name(raw_name: str) -> VaultName:
        try:
            return VaultName(raw_name)
        except VaultDomainError as exc:
            raise VaultValidationError(str(exc)) from exc

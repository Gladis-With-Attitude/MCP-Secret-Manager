from __future__ import annotations

from application.audit.use_cases import NoopAuditRecorder, record_audit_event
from application.unit_of_work import UnitOfWork
from application.vault.dto import CreateVaultRequest, VaultResponse
from application.vault.exceptions import VaultAlreadyExistsError, VaultValidationError
from domain.audit.repositories import AuditRecorder
from domain.audit.value_objects import AuditResult
from domain.vault.entities import Vault
from domain.vault.exceptions import VaultDomainError
from domain.vault.repositories import VaultRepositoryConflictError
from domain.vault.value_objects import VaultName


class CreateVaultUseCase:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        audit_recorder: AuditRecorder | None = None,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._audit_recorder = audit_recorder or NoopAuditRecorder()

    async def execute(self, request: CreateVaultRequest) -> VaultResponse:
        try:
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
        except Exception:
            await record_audit_event(
                self._audit_recorder,
                request.audit_context,
                action="vault.create",
                resource_type="vault",
                resource_id=None,
                result=AuditResult.FAILURE,
                metadata={"name": request.name},
            )
            raise

        await record_audit_event(
            self._audit_recorder,
            request.audit_context,
            action="vault.create",
            resource_type="vault",
            resource_id=str(created_vault.id),
            result=AuditResult.SUCCESS,
            metadata={"name": created_vault.name.value},
        )

        return VaultResponse.from_domain(created_vault)

    @staticmethod
    def _validate_name(raw_name: str) -> VaultName:
        try:
            return VaultName(raw_name)
        except VaultDomainError as exc:
            raise VaultValidationError(str(exc)) from exc


class ListVaultsUseCase:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def execute(self) -> tuple[VaultResponse, ...]:
        async with self._unit_of_work as unit_of_work:
            vaults = await unit_of_work.vaults.list()
        return tuple(VaultResponse.from_domain(vault) for vault in vaults)

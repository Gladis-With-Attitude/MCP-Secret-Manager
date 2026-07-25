from __future__ import annotations

import logging

from application.audit.use_cases import NoopAuditRecorder, record_audit_event
from application.observability import log_application_event
from application.unit_of_work import UnitOfWork
from application.vault.dto import (
    ArchiveVaultRequest,
    CreateVaultRequest,
    GetVaultRequest,
    ListVaultsRequest,
    PaginationResponse,
    UpdateVaultRequest,
    VaultListResponse,
    VaultPermissionsResponse,
    VaultResponse,
)
from application.vault.exceptions import (
    VaultAlreadyExistsError,
    VaultArchivedError,
    VaultNotFoundError,
    VaultValidationError,
)
from domain.audit.repositories import AuditRecorder
from domain.audit.value_objects import AuditResult
from domain.vault.entities import Vault
from domain.vault.exceptions import VaultDomainError
from domain.vault.repositories import VaultRepositoryConflictError
from domain.vault.value_objects import VaultDescription, VaultId, VaultName

logger = logging.getLogger(__name__)


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
            description = self._validate_description(request.description)

            async with self._unit_of_work as unit_of_work:
                if await unit_of_work.vaults.exists_by_name(name):
                    raise VaultAlreadyExistsError("A vault with this name already exists.")

                vault = Vault.create(name=name, description=description)

                try:
                    created_vault = await unit_of_work.vaults.create(vault)
                except VaultRepositoryConflictError as exc:
                    raise VaultAlreadyExistsError("A vault with this name already exists.") from exc

                await unit_of_work.commit()
        except Exception:
            log_application_event(
                logger,
                event="vault_create",
                result=AuditResult.FAILURE,
            )
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

        log_application_event(
            logger,
            event="vault_create",
            result=AuditResult.SUCCESS,
            resource_id=str(created_vault.id),
            description_configured=created_vault.description.value is not None,
        )
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

    @staticmethod
    def _validate_description(raw_description: str | None) -> VaultDescription:
        try:
            return VaultDescription(raw_description)
        except VaultDomainError as exc:
            raise VaultValidationError(str(exc)) from exc

    @staticmethod
    def _validate_vault_id(raw_vault_id: str) -> VaultId:
        try:
            return VaultId.from_string(raw_vault_id)
        except ValueError as exc:
            raise VaultValidationError("Vault id must be a valid UUID.") from exc


class ListVaultsUseCase:
    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def execute(self, request: ListVaultsRequest | None = None) -> VaultListResponse:
        filters = request or ListVaultsRequest()
        page = self._validate_page(filters.page)
        page_size = self._validate_page_size(filters.page_size)
        status = self._validate_status(filters.status)
        if status is None and filters.locked is True:
            status = "locked"
        include_archived = bool(filters.archived) or status == "archived"
        offset = (page - 1) * page_size

        async with self._unit_of_work as unit_of_work:
            total = await unit_of_work.vaults.count(
                include_archived=include_archived,
                search=filters.search,
                status=status,
            )
            vaults = await unit_of_work.vaults.list(
                include_archived=include_archived,
                limit=page_size,
                offset=offset,
                search=filters.search,
                status=status,
            )

        return VaultListResponse(
            data=tuple(VaultResponse.from_domain(vault) for vault in vaults),
            pagination=PaginationResponse(
                page=page,
                page_size=page_size,
                total=total,
                has_next_page=offset + page_size < total,
                has_previous_page=page > 1,
            ),
            permissions=VaultPermissionsResponse(
                create=True,
                read=True,
                update=True,
                archive=True,
                lock=False,
            ),
        )

    @staticmethod
    def _validate_page(raw_page: int) -> int:
        if raw_page < 1:
            raise VaultValidationError("Page must be greater than or equal to 1.")
        return raw_page

    @staticmethod
    def _validate_page_size(raw_page_size: int) -> int:
        if raw_page_size < 1 or raw_page_size > 100:
            raise VaultValidationError("Page size must be between 1 and 100.")
        return raw_page_size

    @staticmethod
    def _validate_status(raw_status: str | None) -> str | None:
        if raw_status is None:
            return None
        normalized_status = raw_status.strip().lower()
        if normalized_status in {"active", "archived", "locked"}:
            return normalized_status
        raise VaultValidationError("Vault status filter is invalid.")


class GetVaultUseCase:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        audit_recorder: AuditRecorder | None = None,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._audit_recorder = audit_recorder or NoopAuditRecorder()

    async def execute(self, request: GetVaultRequest) -> VaultResponse:
        try:
            vault_id = CreateVaultUseCase._validate_vault_id(request.vault_id)
            async with self._unit_of_work as unit_of_work:
                vault = await unit_of_work.vaults.get(vault_id)
                if vault is None:
                    raise VaultNotFoundError("Vault not found.")
        except Exception:
            log_application_event(
                logger,
                event="vault_get",
                result=AuditResult.FAILURE,
                resource_id=request.vault_id,
            )
            await record_audit_event(
                self._audit_recorder,
                request.audit_context,
                action="vault.read",
                resource_type="vault",
                resource_id=request.vault_id,
                result=AuditResult.FAILURE,
                metadata={},
            )
            raise

        log_application_event(
            logger,
            event="vault_get",
            result=AuditResult.SUCCESS,
            resource_id=str(vault.id),
            archived=vault.archived,
            locked=vault.locked,
        )
        await record_audit_event(
            self._audit_recorder,
            request.audit_context,
            action="vault.read",
            resource_type="vault",
            resource_id=str(vault.id),
            result=AuditResult.SUCCESS,
            metadata={},
        )

        return VaultResponse.from_domain(vault)


class UpdateVaultUseCase:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        audit_recorder: AuditRecorder | None = None,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._audit_recorder = audit_recorder or NoopAuditRecorder()

    async def execute(self, request: UpdateVaultRequest) -> VaultResponse:
        try:
            vault_id = CreateVaultUseCase._validate_vault_id(request.vault_id)
            name = CreateVaultUseCase._validate_name(request.name)
            description = CreateVaultUseCase._validate_description(request.description)

            async with self._unit_of_work as unit_of_work:
                vault = await unit_of_work.vaults.get(vault_id)
                if vault is None:
                    raise VaultNotFoundError("Vault not found.")
                if vault.archived:
                    raise VaultArchivedError("Archived vaults cannot be updated.")
                if await unit_of_work.vaults.exists_by_name(name, exclude_vault_id=vault_id):
                    raise VaultAlreadyExistsError("A vault with this name already exists.")

                try:
                    updated_vault = await unit_of_work.vaults.update(
                        vault.update_metadata(name=name, description=description)
                    )
                except VaultRepositoryConflictError as exc:
                    raise VaultAlreadyExistsError("A vault with this name already exists.") from exc

                await unit_of_work.commit()
        except Exception:
            log_application_event(
                logger,
                event="vault_update",
                result=AuditResult.FAILURE,
                resource_id=request.vault_id,
            )
            await record_audit_event(
                self._audit_recorder,
                request.audit_context,
                action="vault.update",
                resource_type="vault",
                resource_id=request.vault_id,
                result=AuditResult.FAILURE,
                metadata={"name": request.name},
            )
            raise

        log_application_event(
            logger,
            event="vault_update",
            result=AuditResult.SUCCESS,
            resource_id=str(updated_vault.id),
            description_configured=updated_vault.description.value is not None,
        )
        await record_audit_event(
            self._audit_recorder,
            request.audit_context,
            action="vault.update",
            resource_type="vault",
            resource_id=str(updated_vault.id),
            result=AuditResult.SUCCESS,
            metadata={"name": updated_vault.name.value},
        )

        return VaultResponse.from_domain(updated_vault)


class ArchiveVaultUseCase:
    def __init__(
        self,
        unit_of_work: UnitOfWork,
        audit_recorder: AuditRecorder | None = None,
    ) -> None:
        self._unit_of_work = unit_of_work
        self._audit_recorder = audit_recorder or NoopAuditRecorder()

    async def execute(self, request: ArchiveVaultRequest) -> VaultResponse:
        try:
            vault_id = CreateVaultUseCase._validate_vault_id(request.vault_id)
            async with self._unit_of_work as unit_of_work:
                vault = await unit_of_work.vaults.get(vault_id)
                if vault is None:
                    raise VaultNotFoundError("Vault not found.")

                archived_vault = (
                    vault if vault.archived else await unit_of_work.vaults.update(vault.archive())
                )
                await unit_of_work.commit()
        except Exception:
            log_application_event(
                logger,
                event="vault_archive",
                result=AuditResult.FAILURE,
                resource_id=request.vault_id,
            )
            await record_audit_event(
                self._audit_recorder,
                request.audit_context,
                action="vault.archive",
                resource_type="vault",
                resource_id=request.vault_id,
                result=AuditResult.FAILURE,
                metadata={},
            )
            raise

        log_application_event(
            logger,
            event="vault_archive",
            result=AuditResult.SUCCESS,
            resource_id=str(archived_vault.id),
            already_archived=vault.archived,
        )
        await record_audit_event(
            self._audit_recorder,
            request.audit_context,
            action="vault.archive",
            resource_type="vault",
            resource_id=str(archived_vault.id),
            result=AuditResult.SUCCESS,
            metadata={},
        )

        return VaultResponse.from_domain(archived_vault)

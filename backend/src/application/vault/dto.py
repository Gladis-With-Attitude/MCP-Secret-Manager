from __future__ import annotations

from dataclasses import dataclass

from application.audit.dto import AuditContext
from domain.vault.entities import Vault


@dataclass(frozen=True, slots=True)
class CreateVaultRequest:
    name: str
    description: str | None = None
    audit_context: AuditContext | None = None


@dataclass(frozen=True, slots=True)
class ListVaultsRequest:
    page: int = 1
    page_size: int = 20
    search: str | None = None
    status: str | None = None
    archived: bool | None = None
    locked: bool | None = None


@dataclass(frozen=True, slots=True)
class GetVaultRequest:
    vault_id: str
    audit_context: AuditContext | None = None


@dataclass(frozen=True, slots=True)
class UpdateVaultRequest:
    vault_id: str
    name: str
    description: str | None = None
    audit_context: AuditContext | None = None


@dataclass(frozen=True, slots=True)
class ArchiveVaultRequest:
    vault_id: str
    audit_context: AuditContext | None = None


@dataclass(frozen=True, slots=True)
class VaultResponse:
    id: str
    name: str
    description: str | None = None
    archived: bool = False
    locked: bool = False
    status: str = "active"
    created_at: str = ""
    updated_at: str = ""
    archived_at: str | None = None

    @classmethod
    def from_domain(cls, vault: Vault) -> VaultResponse:
        status = "archived" if vault.archived else "locked" if vault.locked else "active"
        return cls(
            id=str(vault.id),
            name=vault.name.value,
            description=vault.description.value,
            archived=vault.archived,
            locked=vault.locked,
            status=status,
            created_at=vault.created_at.isoformat(),
            updated_at=vault.updated_at.isoformat(),
            archived_at=vault.archived_at.isoformat() if vault.archived_at else None,
        )


@dataclass(frozen=True, slots=True)
class VaultPermissionsResponse:
    create: bool
    read: bool
    update: bool
    archive: bool
    lock: bool


@dataclass(frozen=True, slots=True)
class PaginationResponse:
    page: int
    page_size: int
    total: int
    has_next_page: bool
    has_previous_page: bool


@dataclass(frozen=True, slots=True)
class VaultListResponse:
    data: tuple[VaultResponse, ...]
    pagination: PaginationResponse
    permissions: VaultPermissionsResponse

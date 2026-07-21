from __future__ import annotations

from dataclasses import dataclass

from application.audit.dto import AuditContext
from domain.vault.entities import Vault


@dataclass(frozen=True, slots=True)
class CreateVaultRequest:
    name: str
    audit_context: AuditContext | None = None


@dataclass(frozen=True, slots=True)
class VaultResponse:
    id: str
    name: str

    @classmethod
    def from_domain(cls, vault: Vault) -> VaultResponse:
        return cls(id=str(vault.id), name=vault.name.value)

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from domain.vault.entities import Vault
from domain.vault.value_objects import VaultId, VaultName


class VaultRepositoryConflictError(RuntimeError):
    """Raised when persistence detects a Vault uniqueness conflict."""


class VaultRepository(Protocol):
    async def create(self, vault: Vault) -> Vault:
        raise NotImplementedError

    async def get(self, vault_id: VaultId) -> Vault | None:
        raise NotImplementedError

    async def list(self) -> Sequence[Vault]:
        raise NotImplementedError

    async def exists_by_name(self, name: VaultName) -> bool:
        raise NotImplementedError

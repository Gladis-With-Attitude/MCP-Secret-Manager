from __future__ import annotations

from dataclasses import dataclass

from domain.vault.value_objects import VaultId, VaultName


@dataclass(frozen=True, slots=True, eq=False)
class Vault:
    id: VaultId
    name: VaultName

    @classmethod
    def create(cls, name: VaultName) -> Vault:
        return cls(id=VaultId.new(), name=name)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vault):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

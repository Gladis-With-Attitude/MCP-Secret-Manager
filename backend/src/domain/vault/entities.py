from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import UTC, datetime

from domain.vault.value_objects import VaultDescription, VaultId, VaultName


@dataclass(frozen=True, slots=True, eq=False)
class Vault:
    id: VaultId
    name: VaultName
    description: VaultDescription = field(default_factory=lambda: VaultDescription(None))
    archived: bool = False
    locked: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    archived_at: datetime | None = None

    @classmethod
    def create(cls, name: VaultName, description: VaultDescription | None = None) -> Vault:
        now = datetime.now(UTC)
        return cls(
            id=VaultId.new(),
            name=name,
            description=description or VaultDescription(None),
            archived=False,
            locked=False,
            created_at=now,
            updated_at=now,
            archived_at=None,
        )

    def update_metadata(self, name: VaultName, description: VaultDescription) -> Vault:
        return replace(
            self,
            name=name,
            description=description,
            updated_at=datetime.now(UTC),
        )

    def archive(self) -> Vault:
        now = datetime.now(UTC)
        return replace(self, archived=True, updated_at=now, archived_at=now)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Vault):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

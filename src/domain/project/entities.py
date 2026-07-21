from __future__ import annotations

from dataclasses import dataclass

from domain.project.value_objects import ProjectId, ProjectName
from domain.vault.value_objects import VaultId


@dataclass(frozen=True, slots=True, eq=False)
class Project:
    id: ProjectId
    vault_id: VaultId
    name: ProjectName

    @classmethod
    def create(cls, vault_id: VaultId, name: ProjectName) -> Project:
        return cls(id=ProjectId.new(), vault_id=vault_id, name=name)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Project):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

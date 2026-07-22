from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import UTC, datetime

from domain.project.value_objects import ProjectDescription, ProjectId, ProjectName
from domain.vault.value_objects import VaultId


@dataclass(frozen=True, slots=True, eq=False)
class Project:
    id: ProjectId
    vault_id: VaultId
    name: ProjectName
    description: ProjectDescription = field(default_factory=lambda: ProjectDescription(None))
    archived: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    archived_at: datetime | None = None

    @classmethod
    def create(
        cls,
        vault_id: VaultId,
        name: ProjectName,
        description: ProjectDescription | None = None,
    ) -> Project:
        now = datetime.now(UTC)
        return cls(
            id=ProjectId.new(),
            vault_id=vault_id,
            name=name,
            description=description or ProjectDescription(None),
            archived=False,
            created_at=now,
            updated_at=now,
            archived_at=None,
        )

    def update_metadata(self, name: ProjectName, description: ProjectDescription) -> Project:
        return replace(
            self,
            name=name,
            description=description,
            updated_at=datetime.now(UTC),
        )

    def archive(self) -> Project:
        now = datetime.now(UTC)
        return replace(self, archived=True, updated_at=now, archived_at=now)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Project):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

from __future__ import annotations

from dataclasses import dataclass

from domain.project.value_objects import ProjectId
from domain.secret.value_objects import SecretDescription, SecretId, SecretKey


@dataclass(frozen=True, slots=True, eq=False)
class Secret:
    id: SecretId
    project_id: ProjectId
    key: SecretKey
    description: SecretDescription

    @classmethod
    def create(
        cls,
        project_id: ProjectId,
        key: SecretKey,
        description: SecretDescription,
    ) -> Secret:
        return cls(id=SecretId.new(), project_id=project_id, key=key, description=description)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Secret):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

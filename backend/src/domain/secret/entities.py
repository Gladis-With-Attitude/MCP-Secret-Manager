from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import UTC, datetime

from domain.project.value_objects import ProjectId
from domain.secret.value_objects import (
    SecretDescription,
    SecretId,
    SecretKey,
    SecretMetadataObject,
    SecretTags,
    SecretType,
)


@dataclass(frozen=True, slots=True, eq=False)
class Secret:
    id: SecretId
    project_id: ProjectId
    key: SecretKey
    description: SecretDescription
    type: SecretType = field(default_factory=lambda: SecretType("generic"))
    metadata: SecretMetadataObject = field(default_factory=lambda: SecretMetadataObject({}))
    tags: SecretTags = field(default_factory=lambda: SecretTags(()))
    archived: bool = False
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    archived_at: datetime | None = None

    @classmethod
    def create(
        cls,
        project_id: ProjectId,
        key: SecretKey,
        description: SecretDescription,
        secret_type: SecretType | None = None,
        metadata: SecretMetadataObject | None = None,
        tags: SecretTags | None = None,
    ) -> Secret:
        now = datetime.now(UTC)
        return cls(
            id=SecretId.new(),
            project_id=project_id,
            key=key,
            description=description,
            type=secret_type or SecretType("generic"),
            metadata=metadata or SecretMetadataObject({}),
            tags=tags or SecretTags(()),
            archived=False,
            created_at=now,
            updated_at=now,
            archived_at=None,
        )

    def update_metadata(
        self,
        key: SecretKey,
        description: SecretDescription,
        secret_type: SecretType,
        metadata: SecretMetadataObject,
        tags: SecretTags,
    ) -> Secret:
        return replace(
            self,
            key=key,
            description=description,
            type=secret_type,
            metadata=metadata,
            tags=tags,
            updated_at=datetime.now(UTC),
        )

    def archive(self) -> Secret:
        now = datetime.now(UTC)
        return replace(self, archived=True, updated_at=now, archived_at=now)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Secret):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

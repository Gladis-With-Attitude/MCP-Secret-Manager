from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.project.value_objects import ProjectId
from domain.secret.entities import Secret
from domain.secret.value_objects import (
    SecretDescription,
    SecretId,
    SecretKey,
    SecretMetadata,
    SecretMetadataObject,
    SecretTags,
    SecretType,
)
from infrastructure.persistence.base import Base

if TYPE_CHECKING:
    from infrastructure.persistence.project_model import ProjectModel
    from infrastructure.persistence.secret_version_model import SecretVersionModel


class SecretModel(Base):
    __tablename__ = "secrets"
    __table_args__ = (
        UniqueConstraint("project_id", "key", name="uq_secrets_project_id_key"),
        CheckConstraint(
            "char_length(key) >= 3 AND char_length(key) <= 128",
            name="ck_secrets_key_length",
        ),
        CheckConstraint("key ~ '^[A-Z0-9_]+$'", name="ck_secrets_key_format"),
        Index("ix_secrets_project_id", "project_id"),
        Index("ix_secrets_archived", "archived"),
        Index("ix_secrets_type", "type"),
    )

    id: Mapped[UUID] = mapped_column(postgresql.UUID(as_uuid=True), primary_key=True)
    project_id: Mapped[UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("projects.id", name="fk_secrets_project_id_projects", ondelete="RESTRICT"),
        nullable=False,
    )
    key: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    type: Mapped[str] = mapped_column(String(40), nullable=False)
    metadata_json: Mapped[SecretMetadata] = mapped_column(
        "metadata",
        postgresql.JSONB,
        nullable=False,
    )
    tags: Mapped[list[str]] = mapped_column(postgresql.JSONB, nullable=False)
    archived: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    project: Mapped[ProjectModel] = relationship("ProjectModel", back_populates="secrets")
    versions: Mapped[list[SecretVersionModel]] = relationship(
        "SecretVersionModel",
        back_populates="secret",
    )

    @classmethod
    def from_domain(cls, secret: Secret) -> SecretModel:
        return cls(
            id=secret.id.value,
            project_id=secret.project_id.value,
            key=secret.key.value,
            description=secret.description.value,
            type=secret.type.value,
            metadata_json=secret.metadata.value,
            tags=list(secret.tags.value),
            archived=secret.archived,
            created_at=secret.created_at,
            updated_at=secret.updated_at,
            archived_at=secret.archived_at,
        )

    def to_domain(self) -> Secret:
        return Secret(
            id=SecretId(self.id),
            project_id=ProjectId(self.project_id),
            key=SecretKey(self.key),
            description=SecretDescription(self.description),
            type=SecretType(self.type),
            metadata=SecretMetadataObject(dict(self.metadata_json)),
            tags=SecretTags(tuple(self.tags)),
            archived=self.archived,
            created_at=self.created_at,
            updated_at=self.updated_at,
            archived_at=self.archived_at,
        )

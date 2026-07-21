from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.project.value_objects import ProjectId
from domain.secret.entities import Secret
from domain.secret.value_objects import SecretDescription, SecretId, SecretKey
from infrastructure.persistence.base import Base

if TYPE_CHECKING:
    from infrastructure.persistence.project_model import ProjectModel


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
    )

    id: Mapped[UUID] = mapped_column(postgresql.UUID(as_uuid=True), primary_key=True)
    project_id: Mapped[UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("projects.id", name="fk_secrets_project_id_projects", ondelete="RESTRICT"),
        nullable=False,
    )
    key: Mapped[str] = mapped_column(String(128), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    project: Mapped[ProjectModel] = relationship("ProjectModel", back_populates="secrets")

    @classmethod
    def from_domain(cls, secret: Secret) -> SecretModel:
        return cls(
            id=secret.id.value,
            project_id=secret.project_id.value,
            key=secret.key.value,
            description=secret.description.value,
        )

    def to_domain(self) -> Secret:
        return Secret(
            id=SecretId(self.id),
            project_id=ProjectId(self.project_id),
            key=SecretKey(self.key),
            description=SecretDescription(self.description),
        )

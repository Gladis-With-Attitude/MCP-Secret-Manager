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

from domain.project.entities import Project
from domain.project.value_objects import ProjectDescription, ProjectId, ProjectName
from domain.vault.value_objects import VaultId
from infrastructure.persistence.base import Base

if TYPE_CHECKING:
    from infrastructure.persistence.secret_model import SecretModel
    from infrastructure.persistence.vault_model import VaultModel


class ProjectModel(Base):
    __tablename__ = "projects"
    __table_args__ = (
        UniqueConstraint("vault_id", "name", name="uq_projects_vault_id_name"),
        CheckConstraint(
            "char_length(name) >= 3 AND char_length(name) <= 100",
            name="ck_projects_name_length",
        ),
        CheckConstraint("name = btrim(name)", name="ck_projects_name_trimmed"),
        Index("ix_projects_vault_id", "vault_id"),
        Index("ix_projects_archived", "archived"),
    )

    id: Mapped[UUID] = mapped_column(postgresql.UUID(as_uuid=True), primary_key=True)
    vault_id: Mapped[UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("vaults.id", name="fk_projects_vault_id_vaults", ondelete="RESTRICT"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    archived: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    archived_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    vault: Mapped[VaultModel] = relationship("VaultModel", back_populates="projects")
    secrets: Mapped[list[SecretModel]] = relationship("SecretModel", back_populates="project")

    @classmethod
    def from_domain(cls, project: Project) -> ProjectModel:
        return cls(
            id=project.id.value,
            vault_id=project.vault_id.value,
            name=project.name.value,
            description=project.description.value,
            archived=project.archived,
            created_at=project.created_at,
            updated_at=project.updated_at,
            archived_at=project.archived_at,
        )

    def to_domain(self) -> Project:
        return Project(
            id=ProjectId(self.id),
            vault_id=VaultId(self.vault_id),
            name=ProjectName(self.name),
            description=ProjectDescription(self.description),
            archived=self.archived,
            created_at=self.created_at,
            updated_at=self.updated_at,
            archived_at=self.archived_at,
        )

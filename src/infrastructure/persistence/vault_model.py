from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, String, UniqueConstraint
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.vault.entities import Vault
from domain.vault.value_objects import VaultId, VaultName
from infrastructure.persistence.base import Base

if TYPE_CHECKING:
    from infrastructure.persistence.project_model import ProjectModel


class VaultModel(Base):
    __tablename__ = "vaults"
    __table_args__ = (
        UniqueConstraint("name", name="uq_vaults_name"),
        CheckConstraint(
            "char_length(name) >= 3 AND char_length(name) <= 100",
            name="ck_vaults_name_length",
        ),
        CheckConstraint("name = btrim(name)", name="ck_vaults_name_trimmed"),
    )

    id: Mapped[UUID] = mapped_column(postgresql.UUID(as_uuid=True), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)

    projects: Mapped[list[ProjectModel]] = relationship("ProjectModel", back_populates="vault")

    @classmethod
    def from_domain(cls, vault: Vault) -> VaultModel:
        return cls(id=vault.id.value, name=vault.name.value)

    def to_domain(self) -> Vault:
        return Vault(id=VaultId(self.id), name=VaultName(self.name))

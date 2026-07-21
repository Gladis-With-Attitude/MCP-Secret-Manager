from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, Text, text
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.secret.value_objects import SecretId
from domain.secret_version.entities import SecretVersion
from domain.secret_version.value_objects import (
    SecretValue,
    SecretVersionId,
    SecretVersionNumber,
)
from infrastructure.persistence.base import Base

if TYPE_CHECKING:
    from infrastructure.persistence.secret_model import SecretModel


class SecretVersionModel(Base):
    __tablename__ = "secret_versions"
    __table_args__ = (
        CheckConstraint("version >= 1", name="ck_secret_versions_version_positive"),
        CheckConstraint("char_length(value) >= 1", name="ck_secret_versions_value_required"),
        Index("ix_secret_versions_secret_id", "secret_id"),
        Index(
            "uq_secret_versions_active_secret_id",
            "secret_id",
            unique=True,
            postgresql_where=text("active = true"),
        ),
        Index(
            "uq_secret_versions_secret_id_version",
            "secret_id",
            "version",
            unique=True,
        ),
    )

    id: Mapped[UUID] = mapped_column(postgresql.UUID(as_uuid=True), primary_key=True)
    secret_id: Mapped[UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("secrets.id", name="fk_secret_versions_secret_id_secrets", ondelete="RESTRICT"),
        nullable=False,
    )
    value: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    secret: Mapped[SecretModel] = relationship("SecretModel", back_populates="versions")

    @classmethod
    def from_domain(cls, secret_version: SecretVersion) -> SecretVersionModel:
        return cls(
            id=secret_version.id.value,
            secret_id=secret_version.secret_id.value,
            value=secret_version.value.value,
            version=secret_version.version.value,
            active=secret_version.active,
            created_at=secret_version.created_at,
        )

    def to_domain(self) -> SecretVersion:
        return SecretVersion(
            id=SecretVersionId(self.id),
            secret_id=SecretId(self.secret_id),
            value=SecretValue(self.value),
            version=SecretVersionNumber(self.version),
            active=self.active,
            created_at=self.created_at,
        )

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
    Integer,
    LargeBinary,
    String,
    text,
)
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.secret.value_objects import SecretId
from domain.secret_version.entities import SecretVersion
from domain.secret_version.value_objects import (
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
        CheckConstraint(
            "octet_length(encrypted_value) >= 1",
            name="ck_secret_versions_encrypted_value_required",
        ),
        CheckConstraint(
            "octet_length(encrypted_dek) >= 1",
            name="ck_secret_versions_encrypted_dek_required",
        ),
        CheckConstraint(
            "octet_length(nonce) = 12",
            name="ck_secret_versions_nonce_aes_gcm_size",
        ),
        CheckConstraint(
            "octet_length(authentication_tag) = 16",
            name="ck_secret_versions_authentication_tag_aes_gcm_size",
        ),
        CheckConstraint(
            "char_length(encryption_algorithm) >= 1",
            name="ck_secret_versions_encryption_algorithm_required",
        ),
        CheckConstraint("key_version >= 1", name="ck_secret_versions_key_version_positive"),
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
    encrypted_value: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    encrypted_dek: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    nonce: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    authentication_tag: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    encryption_algorithm: Mapped[str] = mapped_column(String(length=64), nullable=False)
    key_version: Mapped[int] = mapped_column(Integer, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    secret: Mapped[SecretModel] = relationship("SecretModel", back_populates="versions")

    @classmethod
    def from_domain(cls, secret_version: SecretVersion) -> SecretVersionModel:
        return cls(
            id=secret_version.id.value,
            secret_id=secret_version.secret_id.value,
            encrypted_value=secret_version.encrypted_value,
            encrypted_dek=secret_version.encrypted_dek,
            nonce=secret_version.nonce,
            authentication_tag=secret_version.authentication_tag,
            encryption_algorithm=secret_version.encryption_algorithm,
            key_version=secret_version.key_version,
            version=secret_version.version.value,
            active=secret_version.active,
            created_at=secret_version.created_at,
        )

    def to_domain(self) -> SecretVersion:
        return SecretVersion(
            id=SecretVersionId(self.id),
            secret_id=SecretId(self.secret_id),
            encrypted_value=self.encrypted_value,
            encrypted_dek=self.encrypted_dek,
            nonce=self.nonce,
            authentication_tag=self.authentication_tag,
            encryption_algorithm=self.encryption_algorithm,
            key_version=self.key_version,
            version=SecretVersionNumber(self.version),
            active=self.active,
            created_at=self.created_at,
        )

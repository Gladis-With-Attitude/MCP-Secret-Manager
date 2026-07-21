from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.identity.entities import ApiKey, ServiceAccount, User
from domain.identity.value_objects import (
    ApiKeyId,
    ApiKeyOwnerType,
    IdentityStatus,
    ServiceAccountId,
    ServiceAccountName,
    UserDisplayName,
    UserEmail,
    UserId,
)
from domain.project.value_objects import ProjectId
from infrastructure.persistence.base import Base

if TYPE_CHECKING:
    from infrastructure.persistence.project_model import ProjectModel


class UserModel(Base):
    __tablename__ = "users"
    __table_args__ = (
        CheckConstraint("char_length(email) >= 3", name="ck_users_email_required"),
        CheckConstraint(
            "char_length(display_name) >= 1",
            name="ck_users_display_name_required",
        ),
        CheckConstraint(
            "status IN ('active', 'disabled')",
            name="ck_users_status_valid",
        ),
        Index("uq_users_email", "email", unique=True),
    )

    id: Mapped[UUID] = mapped_column(postgresql.UUID(as_uuid=True), primary_key=True)
    email: Mapped[str] = mapped_column(String(length=254), nullable=False)
    display_name: Mapped[str] = mapped_column(String(length=100), nullable=False)
    status: Mapped[str] = mapped_column(String(length=32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    @classmethod
    def from_domain(cls, user: User) -> UserModel:
        return cls(
            id=user.id.value,
            email=user.email.value,
            display_name=user.display_name.value,
            status=user.status.value,
            created_at=user.created_at,
        )

    def to_domain(self) -> User:
        return User(
            id=UserId(self.id),
            email=UserEmail(self.email),
            display_name=UserDisplayName(self.display_name),
            status=IdentityStatus(self.status),
            created_at=self.created_at,
        )


class ServiceAccountModel(Base):
    __tablename__ = "service_accounts"
    __table_args__ = (
        CheckConstraint("char_length(name) >= 3", name="ck_service_accounts_name_min_length"),
        CheckConstraint(
            "status IN ('active', 'disabled')",
            name="ck_service_accounts_status_valid",
        ),
        Index(
            "uq_service_accounts_project_id_name",
            "project_id",
            "name",
            unique=True,
        ),
        Index("ix_service_accounts_project_id", "project_id"),
    )

    id: Mapped[UUID] = mapped_column(postgresql.UUID(as_uuid=True), primary_key=True)
    project_id: Mapped[UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("projects.id", name="fk_service_accounts_project_id_projects"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(length=100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(length=32), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    project: Mapped[ProjectModel] = relationship("ProjectModel")

    @classmethod
    def from_domain(cls, service_account: ServiceAccount) -> ServiceAccountModel:
        return cls(
            id=service_account.id.value,
            project_id=service_account.project_id.value,
            name=service_account.name.value,
            description=service_account.description,
            status=service_account.status.value,
            created_at=service_account.created_at,
        )

    def to_domain(self) -> ServiceAccount:
        return ServiceAccount(
            id=ServiceAccountId(self.id),
            project_id=ProjectId(self.project_id),
            name=ServiceAccountName(self.name),
            description=self.description,
            status=IdentityStatus(self.status),
            created_at=self.created_at,
        )


class ApiKeyModel(Base):
    __tablename__ = "api_keys"
    __table_args__ = (
        CheckConstraint("char_length(hashed_key) >= 1", name="ck_api_keys_hashed_key_required"),
        CheckConstraint("char_length(key_prefix) >= 1", name="ck_api_keys_key_prefix_required"),
        CheckConstraint(
            "owner_type IN ('user', 'service_account')",
            name="ck_api_keys_owner_type_valid",
        ),
        Index("uq_api_keys_key_prefix", "key_prefix", unique=True),
        Index("ix_api_keys_owner", "owner_type", "owner_id"),
    )

    id: Mapped[UUID] = mapped_column(postgresql.UUID(as_uuid=True), primary_key=True)
    hashed_key: Mapped[str] = mapped_column(Text, nullable=False)
    key_prefix: Mapped[str] = mapped_column(String(length=32), nullable=False)
    owner_id: Mapped[UUID] = mapped_column(postgresql.UUID(as_uuid=True), nullable=False)
    owner_type: Mapped[str] = mapped_column(String(length=32), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    @classmethod
    def from_domain(cls, api_key: ApiKey) -> ApiKeyModel:
        return cls(
            id=api_key.id.value,
            hashed_key=api_key.hashed_key,
            key_prefix=api_key.key_prefix,
            owner_id=api_key.owner_id.value,
            owner_type=api_key.owner_type.value,
            expires_at=api_key.expires_at,
            revoked_at=api_key.revoked_at,
            created_at=api_key.created_at,
        )

    def to_domain(self) -> ApiKey:
        owner_type = ApiKeyOwnerType(self.owner_type)
        owner_id: UserId | ServiceAccountId
        if owner_type is ApiKeyOwnerType.USER:
            owner_id = UserId(self.owner_id)
        else:
            owner_id = ServiceAccountId(self.owner_id)

        return ApiKey(
            id=ApiKeyId(self.id),
            hashed_key=self.hashed_key,
            key_prefix=self.key_prefix,
            owner_id=owner_id,
            owner_type=owner_type,
            expires_at=self.expires_at,
            revoked_at=self.revoked_at,
            created_at=self.created_at,
        )

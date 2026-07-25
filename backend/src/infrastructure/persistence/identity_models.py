from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import JSON, Boolean, CheckConstraint, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from domain.identity.entities import ApiKey, AuthSession, ServiceAccount, User, UserPreferences
from domain.identity.value_objects import (
    ApiKeyId,
    ApiKeyOwnerType,
    IdentityStatus,
    ServiceAccountId,
    ServiceAccountName,
    SessionId,
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


class UserPreferencesModel(Base):
    __tablename__ = "user_preferences"
    __table_args__ = (
        CheckConstraint(
            "theme IN ('light', 'dark', 'system')",
            name="ck_user_preferences_theme_valid",
        ),
        CheckConstraint(
            "language IN ('en', 'fr')",
            name="ck_user_preferences_language_valid",
        ),
        CheckConstraint(
            "date_time_format IN ('absolute', 'relative', 'short')",
            name="ck_user_preferences_date_time_format_valid",
        ),
        CheckConstraint(
            "display_density IN ('comfortable', 'compact')",
            name="ck_user_preferences_display_density_valid",
        ),
    )

    user_id: Mapped[UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("users.id", name="fk_user_preferences_user_id_users", ondelete="CASCADE"),
        primary_key=True,
    )
    organization: Mapped[str | None] = mapped_column(String(length=120), nullable=True)
    avatar_url: Mapped[str | None] = mapped_column(String(length=2048), nullable=True)
    theme: Mapped[str] = mapped_column(String(length=32), nullable=False)
    language: Mapped[str] = mapped_column(String(length=16), nullable=False)
    timezone: Mapped[str] = mapped_column(String(length=80), nullable=False)
    date_time_format: Mapped[str] = mapped_column(String(length=32), nullable=False)
    display_density: Mapped[str] = mapped_column(String(length=32), nullable=False)
    audit_alerts: Mapped[bool] = mapped_column(Boolean, nullable=False)
    email_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False)
    in_app_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False)
    product_updates: Mapped[bool] = mapped_column(Boolean, nullable=False)
    security_alerts: Mapped[bool] = mapped_column(Boolean, nullable=False)

    user: Mapped[UserModel] = relationship("UserModel")

    @classmethod
    def from_domain(cls, preferences: UserPreferences) -> UserPreferencesModel:
        return cls(
            user_id=preferences.user_id.value,
            organization=preferences.organization,
            avatar_url=preferences.avatar_url,
            theme=preferences.theme,
            language=preferences.language,
            timezone=preferences.timezone,
            date_time_format=preferences.date_time_format,
            display_density=preferences.display_density,
            audit_alerts=preferences.audit_alerts,
            email_enabled=preferences.email_enabled,
            in_app_enabled=preferences.in_app_enabled,
            product_updates=preferences.product_updates,
            security_alerts=preferences.security_alerts,
        )

    def to_domain(self) -> UserPreferences:
        return UserPreferences(
            user_id=UserId(self.user_id),
            organization=self.organization,
            avatar_url=self.avatar_url,
            theme=self.theme,
            language=self.language,
            timezone=self.timezone,
            date_time_format=self.date_time_format,
            display_density=self.display_density,
            audit_alerts=self.audit_alerts,
            email_enabled=self.email_enabled,
            in_app_enabled=self.in_app_enabled,
            product_updates=self.product_updates,
            security_alerts=self.security_alerts,
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
        CheckConstraint("name IS NULL OR char_length(name) >= 1", name="ck_api_keys_name_valid"),
        CheckConstraint(
            "owner_type IN ('user', 'service_account')",
            name="ck_api_keys_owner_type_valid",
        ),
        Index("uq_api_keys_key_prefix", "key_prefix", unique=True),
        Index("ix_api_keys_owner", "owner_type", "owner_id"),
        Index("ix_api_keys_status", "revoked_at", "expires_at"),
    )

    id: Mapped[UUID] = mapped_column(postgresql.UUID(as_uuid=True), primary_key=True)
    hashed_key: Mapped[str] = mapped_column(Text, nullable=False)
    key_prefix: Mapped[str] = mapped_column(String(length=32), nullable=False)
    owner_id: Mapped[UUID] = mapped_column(postgresql.UUID(as_uuid=True), nullable=False)
    owner_type: Mapped[str] = mapped_column(String(length=32), nullable=False)
    name: Mapped[str | None] = mapped_column(String(length=120), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    granted_permissions: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    scopes: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
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
            name=api_key.name,
            description=api_key.description,
            granted_permissions=list(api_key.granted_permissions),
            scopes=list(api_key.scopes),
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
            name=self.name,
            description=self.description,
            granted_permissions=tuple(self.granted_permissions or []),
            scopes=tuple(self.scopes or []),
            expires_at=self.expires_at,
            revoked_at=self.revoked_at,
            created_at=self.created_at,
        )


class AuthSessionModel(Base):
    __tablename__ = "auth_sessions"
    __table_args__ = (
        CheckConstraint("char_length(hashed_token) >= 1", name="ck_auth_sessions_hash_required"),
        CheckConstraint("char_length(token_prefix) >= 1", name="ck_auth_sessions_prefix_required"),
        CheckConstraint(
            "owner_type IN ('user', 'service_account')",
            name="ck_auth_sessions_owner_type_valid",
        ),
        Index("uq_auth_sessions_token_prefix", "token_prefix", unique=True),
        Index("ix_auth_sessions_api_key_id", "api_key_id"),
        Index("ix_auth_sessions_owner", "owner_type", "owner_id"),
    )

    id: Mapped[UUID] = mapped_column(postgresql.UUID(as_uuid=True), primary_key=True)
    hashed_token: Mapped[str] = mapped_column(Text, nullable=False)
    token_prefix: Mapped[str] = mapped_column(String(length=64), nullable=False)
    api_key_id: Mapped[UUID] = mapped_column(
        postgresql.UUID(as_uuid=True),
        ForeignKey("api_keys.id", name="fk_auth_sessions_api_key_id_api_keys"),
        nullable=False,
    )
    owner_id: Mapped[UUID] = mapped_column(postgresql.UUID(as_uuid=True), nullable=False)
    owner_type: Mapped[str] = mapped_column(String(length=32), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    api_key: Mapped[ApiKeyModel] = relationship("ApiKeyModel")

    @classmethod
    def from_domain(cls, session: AuthSession) -> AuthSessionModel:
        return cls(
            id=session.id.value,
            hashed_token=session.hashed_token,
            token_prefix=session.token_prefix,
            api_key_id=session.api_key_id.value,
            owner_id=session.owner_id.value,
            owner_type=session.owner_type.value,
            expires_at=session.expires_at,
            revoked_at=session.revoked_at,
            created_at=session.created_at,
            last_seen_at=session.last_seen_at,
        )

    def to_domain(self) -> AuthSession:
        owner_type = ApiKeyOwnerType(self.owner_type)
        owner_id: UserId | ServiceAccountId
        if owner_type is ApiKeyOwnerType.USER:
            owner_id = UserId(self.owner_id)
        else:
            owner_id = ServiceAccountId(self.owner_id)

        return AuthSession(
            id=SessionId(self.id),
            hashed_token=self.hashed_token,
            token_prefix=self.token_prefix,
            api_key_id=ApiKeyId(self.api_key_id),
            owner_id=owner_id,
            owner_type=owner_type,
            expires_at=self.expires_at,
            revoked_at=self.revoked_at,
            created_at=self.created_at,
            last_seen_at=self.last_seen_at,
        )

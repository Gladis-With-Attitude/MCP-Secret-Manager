"""Persistence infrastructure."""

from infrastructure.persistence.audit_model import AuditEventModel
from infrastructure.persistence.audit_repository import SqlAlchemyAuditRepository
from infrastructure.persistence.base import Base
from infrastructure.persistence.database import create_database_engine, create_session_factory
from infrastructure.persistence.identity_models import ApiKeyModel, ServiceAccountModel, UserModel
from infrastructure.persistence.identity_repositories import (
    SqlAlchemyApiKeyRepository,
    SqlAlchemyServiceAccountRepository,
    SqlAlchemyUserRepository,
)
from infrastructure.persistence.project_model import ProjectModel
from infrastructure.persistence.project_repository import SqlAlchemyProjectRepository
from infrastructure.persistence.rbac_models import (
    PermissionModel,
    RoleAssignmentModel,
    RoleModel,
    RolePermissionModel,
)
from infrastructure.persistence.rbac_repositories import (
    SqlAlchemyPermissionRepository,
    SqlAlchemyRoleAssignmentRepository,
    SqlAlchemyRoleRepository,
)
from infrastructure.persistence.secret_model import SecretModel
from infrastructure.persistence.secret_repository import SqlAlchemySecretRepository
from infrastructure.persistence.secret_version_model import SecretVersionModel
from infrastructure.persistence.secret_version_repository import SqlAlchemySecretVersionRepository
from infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork
from infrastructure.persistence.vault_model import VaultModel
from infrastructure.persistence.vault_repository import SqlAlchemyVaultRepository

__all__ = [
    "ApiKeyModel",
    "AuditEventModel",
    "Base",
    "PermissionModel",
    "ProjectModel",
    "RoleAssignmentModel",
    "RoleModel",
    "RolePermissionModel",
    "SecretModel",
    "SecretVersionModel",
    "ServiceAccountModel",
    "SqlAlchemyApiKeyRepository",
    "SqlAlchemyAuditRepository",
    "SqlAlchemyPermissionRepository",
    "SqlAlchemyProjectRepository",
    "SqlAlchemyRoleAssignmentRepository",
    "SqlAlchemyRoleRepository",
    "SqlAlchemySecretRepository",
    "SqlAlchemySecretVersionRepository",
    "SqlAlchemyServiceAccountRepository",
    "SqlAlchemyUnitOfWork",
    "SqlAlchemyUserRepository",
    "SqlAlchemyVaultRepository",
    "UserModel",
    "VaultModel",
    "create_database_engine",
    "create_session_factory",
]

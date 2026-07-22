from __future__ import annotations

import logging

from sqlalchemy import select

from domain.identity.entities import ApiKey, ServiceAccount, User
from domain.identity.value_objects import ApiKeyOwnerType, ServiceAccountName
from domain.rbac.entities import Permission, Role, RoleAssignment
from domain.rbac.permissions import DEFAULT_PERMISSIONS
from domain.rbac.value_objects import PermissionName, RoleName, ScopeType
from infrastructure.identity import Argon2idApiKeyHasher, SecureApiKeySecretGenerator
from infrastructure.persistence.identity_models import ServiceAccountModel, UserModel
from infrastructure.persistence.identity_repositories import (
    SqlAlchemyApiKeyRepository,
    SqlAlchemyServiceAccountRepository,
    SqlAlchemyUserRepository,
)
from infrastructure.persistence.project_repository import SqlAlchemyProjectRepository
from infrastructure.persistence.rbac_models import PermissionModel, RoleModel
from infrastructure.persistence.rbac_repositories import (
    SqlAlchemyPermissionRepository,
    SqlAlchemyRoleAssignmentRepository,
    SqlAlchemyRoleRepository,
)
from infrastructure.seed.contracts import SeedContext
from infrastructure.seed.definitions import DEFAULT_ROLES

logger = logging.getLogger(__name__)


class PermissionsSeed:
    name = "permissions"

    async def run(self, context: SeedContext) -> None:
        repository = SqlAlchemyPermissionRepository(context.session)
        for name, description in DEFAULT_PERMISSIONS:
            permission_name = PermissionName(name)
            existing = await repository.get_by_name(permission_name)
            if existing is None:
                await repository.create(Permission.create(permission_name, description))
                continue

            await _update_permission_description(context, name, description)

        logger.info("✓ Permissions initialized")


class RolesSeed:
    name = "roles"

    async def run(self, context: SeedContext) -> None:
        permission_repository = SqlAlchemyPermissionRepository(context.session)
        role_repository = SqlAlchemyRoleRepository(context.session)

        for role_definition in DEFAULT_ROLES:
            role_name = RoleName(role_definition.name)
            role = await role_repository.get_by_name(role_name)
            if role is None:
                role = await role_repository.create(
                    Role.create(role_name, role_definition.description)
                )
            else:
                await _update_role_description(
                    context,
                    role_definition.name,
                    role_definition.description,
                )

            for permission_name in role_definition.permissions:
                permission = await permission_repository.get_by_name(
                    PermissionName(permission_name)
                )
                if permission is None:
                    msg = f"Permission {permission_name!r} is missing before role seeding."
                    raise RuntimeError(msg)
                if not await role_repository.has_permission(role.id, permission.id):
                    await role_repository.add_permission(role.id, permission.id)

        logger.info("✓ Roles initialized")


class AdminSeed:
    name = "admin"

    async def run(self, context: SeedContext) -> None:
        user_repository = SqlAlchemyUserRepository(context.session)
        role_repository = SqlAlchemyRoleRepository(context.session)
        assignment_repository = SqlAlchemyRoleAssignmentRepository(context.session)

        admin = await user_repository.get_by_email(context.settings.admin_email)
        if admin is None:
            admin = await user_repository.create(
                User.create(
                    email=context.settings.admin_email,
                    display_name=context.settings.admin_name,
                )
            )
            logger.info("✓ Administrator created")
        else:
            await _update_user_display_name(
                context,
                email=context.settings.admin_email.value,
                display_name=context.settings.admin_name.value,
            )
            logger.info("✓ Administrator already exists")

        administrator_role = await role_repository.get_by_name(RoleName("administrator"))
        if administrator_role is None:
            msg = "Administrator role is missing before admin seeding."
            raise RuntimeError(msg)

        assignments = await assignment_repository.list_for_identity(
            admin.id,
            ApiKeyOwnerType.USER,
        )
        has_admin_assignment = any(
            assignment.scope_type is ScopeType.GLOBAL
            and assignment.role_id == administrator_role.id
            for assignment in assignments
        )
        if not has_admin_assignment:
            await assignment_repository.create(
                RoleAssignment.create(
                    identity_id=admin.id,
                    identity_type=ApiKeyOwnerType.USER,
                    scope_type=ScopeType.GLOBAL,
                    scope_id=None,
                    role_id=administrator_role.id,
                )
            )
            logger.info("✓ Administrator role assigned")

        if context.settings.admin_password_configured:
            logger.info(
                "Admin password bootstrap is configured but password auth is not available."
            )


class AdminApiKeySeed:
    name = "admin-api-key"

    def __init__(self) -> None:
        self._generator = SecureApiKeySecretGenerator()
        self._hasher = Argon2idApiKeyHasher()

    async def run(self, context: SeedContext) -> None:
        raw_api_key = context.settings.admin_api_key
        if raw_api_key is None:
            logger.info("Admin API key bootstrap skipped")
            return

        key_prefix = self._generator.extract_prefix(raw_api_key)
        if key_prefix is None:
            msg = "Bootstrap admin API key format is invalid."
            raise RuntimeError(msg)

        user_repository = SqlAlchemyUserRepository(context.session)
        api_key_repository = SqlAlchemyApiKeyRepository(context.session)
        admin = await user_repository.get_by_email(context.settings.admin_email)
        if admin is None:
            msg = "Administrator user is missing before API key seeding."
            raise RuntimeError(msg)

        existing = await api_key_repository.get_by_prefix(key_prefix)
        if existing is not None:
            logger.info("✓ Administrator API key already exists")
            return

        await api_key_repository.create(
            ApiKey.create(
                hashed_key=self._hasher.hash(raw_api_key),
                key_prefix=key_prefix,
                owner_id=admin.id,
                owner_type=ApiKeyOwnerType.USER,
                expires_at=None,
            )
        )
        logger.info("✓ Administrator API key initialized")


class ServiceAccountSeed:
    name = "service-account"

    def __init__(self) -> None:
        self._generator = SecureApiKeySecretGenerator()
        self._hasher = Argon2idApiKeyHasher()

    async def run(self, context: SeedContext) -> None:
        if not context.settings.service_account_enabled:
            logger.info("Bootstrap service account skipped")
            return
        if context.settings.service_account_project_id is None:
            msg = "Bootstrap service account project id is required."
            raise RuntimeError(msg)
        if context.settings.service_account_name is None:
            msg = "Bootstrap service account name is required."
            raise RuntimeError(msg)

        project_repository = SqlAlchemyProjectRepository(context.session)
        service_account_repository = SqlAlchemyServiceAccountRepository(context.session)
        project = await project_repository.get(context.settings.service_account_project_id)
        if project is None:
            msg = "Bootstrap service account project does not exist."
            raise RuntimeError(msg)

        service_account = await _get_service_account_by_project_and_name(
            context,
            context.settings.service_account_project_id.value,
            context.settings.service_account_name,
        )
        if service_account is None:
            service_account = await service_account_repository.create(
                ServiceAccount.create(
                    project_id=context.settings.service_account_project_id,
                    name=context.settings.service_account_name,
                    description="Bootstrap service account.",
                )
            )
            logger.info("✓ Bootstrap service account initialized")
        else:
            logger.info("✓ Bootstrap service account already exists")

        await self._ensure_service_account_api_key(context, service_account)

    async def _ensure_service_account_api_key(
        self,
        context: SeedContext,
        service_account: ServiceAccount,
    ) -> None:
        raw_api_key = context.settings.service_account_api_key
        if raw_api_key is None:
            return
        key_prefix = self._generator.extract_prefix(raw_api_key)
        if key_prefix is None:
            msg = "Bootstrap service account API key format is invalid."
            raise RuntimeError(msg)

        api_key_repository = SqlAlchemyApiKeyRepository(context.session)
        existing = await api_key_repository.get_by_prefix(key_prefix)
        if existing is not None:
            logger.info("✓ Bootstrap service account API key already exists")
            return

        await api_key_repository.create(
            ApiKey.create(
                hashed_key=self._hasher.hash(raw_api_key),
                key_prefix=key_prefix,
                owner_id=service_account.id,
                owner_type=ApiKeyOwnerType.SERVICE_ACCOUNT,
                expires_at=None,
            )
        )
        logger.info("✓ Bootstrap service account API key initialized")


async def _update_permission_description(
    context: SeedContext,
    name: str,
    description: str,
) -> None:
    model = await context.session.scalar(
        select(PermissionModel).where(PermissionModel.name == name)
    )
    if model is not None and model.description != description:
        model.description = description


async def _update_role_description(context: SeedContext, name: str, description: str) -> None:
    model = await context.session.scalar(select(RoleModel).where(RoleModel.name == name))
    if model is not None and model.description != description:
        model.description = description


async def _update_user_display_name(context: SeedContext, email: str, display_name: str) -> None:
    model = await context.session.scalar(select(UserModel).where(UserModel.email == email))
    if model is not None and model.display_name != display_name:
        model.display_name = display_name


async def _get_service_account_by_project_and_name(
    context: SeedContext,
    project_id: object,
    name: ServiceAccountName,
) -> ServiceAccount | None:
    model = await context.session.scalar(
        select(ServiceAccountModel).where(
            ServiceAccountModel.project_id == project_id,
            ServiceAccountModel.name == name.value,
        )
    )
    if model is None:
        return None
    return model.to_domain()

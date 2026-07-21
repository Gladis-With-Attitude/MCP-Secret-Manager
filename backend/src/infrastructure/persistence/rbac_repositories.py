from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from domain.identity.value_objects import ApiKeyOwnerType, ServiceAccountId, UserId
from domain.rbac.entities import Permission, Role, RoleAssignment
from domain.rbac.repositories import (
    PermissionRepositoryConflictError,
    RoleAssignmentRepositoryConflictError,
    RoleRepositoryConflictError,
)
from domain.rbac.value_objects import PermissionId, PermissionName, RoleId, RoleName
from infrastructure.persistence.rbac_models import (
    PermissionModel,
    RoleAssignmentModel,
    RoleModel,
    RolePermissionModel,
)


class SqlAlchemyPermissionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, permission: Permission) -> Permission:
        model = PermissionModel.from_domain(permission)
        self._session.add(model)
        try:
            await self._session.flush()
        except IntegrityError as exc:
            raise PermissionRepositoryConflictError("Permission persistence conflict.") from exc
        return model.to_domain()

    async def get(self, permission_id: PermissionId) -> Permission | None:
        model = await self._session.get(PermissionModel, permission_id.value)
        if model is None:
            return None
        return model.to_domain()

    async def get_by_name(self, name: PermissionName) -> Permission | None:
        model = await self._session.scalar(
            select(PermissionModel).where(PermissionModel.name == name.value)
        )
        if model is None:
            return None
        return model.to_domain()


class SqlAlchemyRoleRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, role: Role) -> Role:
        model = RoleModel.from_domain(role)
        self._session.add(model)
        try:
            await self._session.flush()
        except IntegrityError as exc:
            raise RoleRepositoryConflictError("Role persistence conflict.") from exc
        return model.to_domain()

    async def get(self, role_id: RoleId) -> Role | None:
        model = await self._session.get(RoleModel, role_id.value)
        if model is None:
            return None
        return model.to_domain()

    async def get_by_name(self, name: RoleName) -> Role | None:
        model = await self._session.scalar(select(RoleModel).where(RoleModel.name == name.value))
        if model is None:
            return None
        return model.to_domain()

    async def add_permission(self, role_id: RoleId, permission_id: PermissionId) -> None:
        self._session.add(
            RolePermissionModel(role_id=role_id.value, permission_id=permission_id.value)
        )
        try:
            await self._session.flush()
        except IntegrityError as exc:
            raise RoleRepositoryConflictError("RolePermission persistence conflict.") from exc

    async def has_permission(self, role_id: RoleId, permission_id: PermissionId) -> bool:
        result = await self._session.scalar(
            select(RolePermissionModel.role_id)
            .where(
                RolePermissionModel.role_id == role_id.value,
                RolePermissionModel.permission_id == permission_id.value,
            )
            .limit(1)
        )
        return result is not None


class SqlAlchemyRoleAssignmentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, role_assignment: RoleAssignment) -> RoleAssignment:
        model = RoleAssignmentModel.from_domain(role_assignment)
        self._session.add(model)
        try:
            await self._session.flush()
        except IntegrityError as exc:
            raise RoleAssignmentRepositoryConflictError(
                "RoleAssignment persistence conflict."
            ) from exc
        return model.to_domain()

    async def list_for_identity(
        self,
        identity_id: UserId | ServiceAccountId,
        identity_type: ApiKeyOwnerType,
    ) -> Sequence[RoleAssignment]:
        result = await self._session.scalars(
            select(RoleAssignmentModel).where(
                RoleAssignmentModel.identity_id == identity_id.value,
                RoleAssignmentModel.identity_type == identity_type.value,
            )
        )
        return tuple(model.to_domain() for model in result.all())

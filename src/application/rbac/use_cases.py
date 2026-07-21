from __future__ import annotations

from uuid import UUID

from application.rbac.dto import AuthorizationDecision, RequirePermission
from application.rbac.exceptions import AuthorizationDeniedError, RbacValidationError
from application.rbac.unit_of_work import RbacUnitOfWork
from domain.identity.value_objects import ApiKeyOwnerType, ServiceAccountId, UserId
from domain.rbac.entities import RoleAssignment
from domain.rbac.exceptions import RbacDomainError
from domain.rbac.value_objects import PermissionName, ScopeType


class PermissionChecker:
    def __init__(self, unit_of_work: RbacUnitOfWork) -> None:
        self._unit_of_work = unit_of_work

    async def is_allowed(self, request: RequirePermission) -> bool:
        identity_type = self._validate_identity_type(request.identity_type)
        identity_id = self._validate_identity_id(request.identity_id, identity_type)
        permission_name = self._validate_permission_name(request.permission)
        scope_type = self._validate_scope_type(request.scope_type)
        scope_id = self._validate_optional_uuid(request.scope_id, field_name="scope id")
        parent_vault_id = self._validate_optional_uuid(
            request.parent_vault_id,
            field_name="parent vault id",
        )
        parent_project_id = self._validate_optional_uuid(
            request.parent_project_id,
            field_name="parent project id",
        )

        async with self._unit_of_work as unit_of_work:
            permission = await unit_of_work.permissions.get_by_name(permission_name)
            if permission is None:
                return False

            assignments = await unit_of_work.role_assignments.list_for_identity(
                identity_id,
                identity_type,
            )
            for assignment in assignments:
                if not self._scope_applies(
                    assignment,
                    scope_type,
                    scope_id,
                    parent_vault_id,
                    parent_project_id,
                ):
                    continue
                if await unit_of_work.roles.has_permission(assignment.role_id, permission.id):
                    return True

        return False

    @staticmethod
    def _scope_applies(
        assignment: RoleAssignment,
        requested_scope_type: ScopeType,
        requested_scope_id: UUID | None,
        parent_vault_id: UUID | None,
        parent_project_id: UUID | None,
    ) -> bool:
        if assignment.scope_type is ScopeType.GLOBAL:
            return True
        if requested_scope_type is ScopeType.GLOBAL:
            return False
        if assignment.scope_type is requested_scope_type:
            return assignment.scope_id == requested_scope_id
        if assignment.scope_type is ScopeType.VAULT and requested_scope_type is ScopeType.PROJECT:
            return assignment.scope_id == parent_vault_id
        if (
            assignment.scope_type is ScopeType.VAULT
            and requested_scope_type is ScopeType.SECRET_RESOURCE
        ):
            return assignment.scope_id == parent_vault_id
        if (
            assignment.scope_type is ScopeType.PROJECT
            and requested_scope_type is ScopeType.SECRET_RESOURCE
        ):
            return assignment.scope_id == parent_project_id
        return False

    @staticmethod
    def _validate_identity_type(raw_identity_type: str) -> ApiKeyOwnerType:
        try:
            return ApiKeyOwnerType(raw_identity_type)
        except ValueError as exc:
            raise RbacValidationError("Identity type is invalid.") from exc

    @staticmethod
    def _validate_identity_id(
        raw_identity_id: str,
        identity_type: ApiKeyOwnerType,
    ) -> UserId | ServiceAccountId:
        try:
            if identity_type is ApiKeyOwnerType.USER:
                return UserId.from_string(raw_identity_id)
            return ServiceAccountId.from_string(raw_identity_id)
        except ValueError as exc:
            raise RbacValidationError("Identity id must be a valid UUID.") from exc

    @staticmethod
    def _validate_permission_name(raw_permission: str) -> PermissionName:
        try:
            return PermissionName(raw_permission)
        except RbacDomainError as exc:
            raise RbacValidationError(str(exc)) from exc

    @staticmethod
    def _validate_scope_type(raw_scope_type: str) -> ScopeType:
        try:
            return ScopeType(raw_scope_type)
        except ValueError as exc:
            raise RbacValidationError("Scope type is invalid.") from exc

    @staticmethod
    def _validate_optional_uuid(raw_value: str | None, field_name: str) -> UUID | None:
        if raw_value is None:
            return None
        try:
            return UUID(raw_value)
        except ValueError as exc:
            raise RbacValidationError(f"{field_name.capitalize()} must be a valid UUID.") from exc


class AuthorizeUseCase:
    def __init__(self, permission_checker: PermissionChecker) -> None:
        self._permission_checker = permission_checker

    async def execute(self, request: RequirePermission) -> AuthorizationDecision:
        allowed = await self._permission_checker.is_allowed(request)
        if not allowed:
            raise AuthorizationDeniedError("Permission denied.")
        return AuthorizationDecision(allowed=True)

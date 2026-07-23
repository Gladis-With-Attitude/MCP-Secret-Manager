from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from application.audit.dto import AuditContext
from application.rbac.dto import (
    AssignActorRoleRequest,
    CreateRoleRequest,
    GetRoleRequest,
    ListActorRolesRequest,
    ListRolesRequest,
    RevokeActorRoleRequest,
    UpdateRoleRequest,
)
from application.rbac.exceptions import RbacConflictError, RbacNotFoundError, RbacValidationError
from application.rbac.use_cases import (
    AssignActorRoleUseCase,
    CreateRoleUseCase,
    GetRoleUseCase,
    ListActorRolesUseCase,
    ListPermissionsUseCase,
    ListRolesUseCase,
    RevokeActorRoleUseCase,
    UpdateRoleUseCase,
)
from presentation.rest.audit_context import get_audit_context
from presentation.rest.authorization import permission_required
from presentation.rest.dependencies import (
    get_assign_actor_role_use_case,
    get_create_role_use_case,
    get_list_actor_roles_use_case,
    get_list_permissions_use_case,
    get_list_roles_use_case,
    get_revoke_actor_role_use_case,
    get_role_use_case,
    get_update_role_use_case,
)
from presentation.rest.schemas import (
    CreateRoleHttpRequest,
    PermissionListHttpResponse,
    RoleHttpResponse,
    RoleListHttpResponse,
    UpdateRoleHttpRequest,
    UserRoleHttpResponse,
    UserRoleListHttpResponse,
)

router = APIRouter(prefix="/v1", tags=["rbac"])

ListPermissionsUseCaseDependency = Annotated[
    ListPermissionsUseCase,
    Depends(get_list_permissions_use_case),
]
ListRolesUseCaseDependency = Annotated[ListRolesUseCase, Depends(get_list_roles_use_case)]
GetRoleUseCaseDependency = Annotated[GetRoleUseCase, Depends(get_role_use_case)]
CreateRoleUseCaseDependency = Annotated[CreateRoleUseCase, Depends(get_create_role_use_case)]
UpdateRoleUseCaseDependency = Annotated[UpdateRoleUseCase, Depends(get_update_role_use_case)]
ListActorRolesUseCaseDependency = Annotated[
    ListActorRolesUseCase,
    Depends(get_list_actor_roles_use_case),
]
AssignActorRoleUseCaseDependency = Annotated[
    AssignActorRoleUseCase,
    Depends(get_assign_actor_role_use_case),
]
RevokeActorRoleUseCaseDependency = Annotated[
    RevokeActorRoleUseCase,
    Depends(get_revoke_actor_role_use_case),
]
AuditContextDependency = Annotated[AuditContext, Depends(get_audit_context)]


@router.get(
    "/permissions",
    response_model=PermissionListHttpResponse,
    responses={
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "Role read permission is required."},
    },
    dependencies=[Depends(permission_required("role.read", "global"))],
)
async def list_permissions(
    use_case: ListPermissionsUseCaseDependency,
) -> PermissionListHttpResponse:
    response = await use_case.execute()
    return PermissionListHttpResponse.from_application(response)


@router.get(
    "/roles",
    response_model=RoleListHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid role list filters."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "Role read permission is required."},
    },
    dependencies=[Depends(permission_required("role.read", "global"))],
)
async def list_roles(
    use_case: ListRolesUseCaseDependency,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
    search: str | None = None,
    q: str | None = None,
    kind: str | None = None,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
) -> RoleListHttpResponse:
    try:
        response = await use_case.execute(
            ListRolesRequest(
                limit=limit,
                offset=offset,
                search=search or q,
                kind=kind,
                status=status_filter,
            )
        )
    except RbacValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return RoleListHttpResponse.from_application(response)


@router.post(
    "/roles",
    status_code=status.HTTP_201_CREATED,
    response_model=RoleHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid role data."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "Role create permission is required."},
        status.HTTP_404_NOT_FOUND: {"description": "Permission not found."},
        status.HTTP_409_CONFLICT: {"description": "Role already exists."},
    },
    dependencies=[Depends(permission_required("role.create", "global"))],
)
async def create_role(
    payload: CreateRoleHttpRequest,
    use_case: CreateRoleUseCaseDependency,
    audit_context: AuditContextDependency,
) -> RoleHttpResponse:
    try:
        response = await use_case.execute(
            CreateRoleRequest(
                name=payload.name,
                description=payload.description,
                permission_ids=tuple(payload.permission_ids),
                audit_context=audit_context,
            )
        )
    except RbacValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RbacNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except RbacConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return RoleHttpResponse.from_application(response)


@router.get(
    "/roles/{role_id}",
    response_model=RoleHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid role id."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "Role read permission is required."},
        status.HTTP_404_NOT_FOUND: {"description": "Role not found."},
    },
    dependencies=[Depends(permission_required("role.read", "global"))],
)
async def get_role(
    role_id: str,
    use_case: GetRoleUseCaseDependency,
    audit_context: AuditContextDependency,
) -> RoleHttpResponse:
    try:
        response = await use_case.execute(GetRoleRequest(role_id, audit_context=audit_context))
    except RbacValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RbacNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return RoleHttpResponse.from_application(response)


@router.patch(
    "/roles/{role_id}",
    response_model=RoleHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid role data."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "Role update permission is required."},
        status.HTTP_404_NOT_FOUND: {"description": "Role or permission not found."},
        status.HTTP_409_CONFLICT: {"description": "Role conflict."},
    },
    dependencies=[Depends(permission_required("role.update", "global"))],
)
async def update_role(
    role_id: str,
    payload: UpdateRoleHttpRequest,
    use_case: UpdateRoleUseCaseDependency,
    audit_context: AuditContextDependency,
) -> RoleHttpResponse:
    try:
        response = await use_case.execute(
            UpdateRoleRequest(
                role_id=role_id,
                name=payload.name,
                description=payload.description,
                permission_ids=tuple(payload.permission_ids),
                audit_context=audit_context,
            )
        )
    except RbacValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RbacNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except RbacConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return RoleHttpResponse.from_application(response)


@router.get(
    "/actors/{actor_id}/roles",
    response_model=UserRoleListHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid actor filters."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "Role read permission is required."},
        status.HTTP_404_NOT_FOUND: {"description": "Actor not found."},
    },
    dependencies=[Depends(permission_required("role.read", "global"))],
)
async def list_actor_roles(
    actor_id: str,
    use_case: ListActorRolesUseCaseDependency,
    identity_type: str = "user",
) -> UserRoleListHttpResponse:
    try:
        response = await use_case.execute(
            ListActorRolesRequest(actor_id=actor_id, identity_type=identity_type)
        )
    except RbacValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RbacNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return UserRoleListHttpResponse.from_application(response)


@router.post(
    "/actors/{actor_id}/roles/{role_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=UserRoleHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid role assignment data."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "Role assign permission is required."},
        status.HTTP_404_NOT_FOUND: {"description": "Actor or role not found."},
        status.HTTP_409_CONFLICT: {"description": "Role assignment already exists."},
    },
    dependencies=[Depends(permission_required("role.assign", "global"))],
)
async def assign_actor_role(
    actor_id: str,
    role_id: str,
    use_case: AssignActorRoleUseCaseDependency,
    audit_context: AuditContextDependency,
    identity_type: str = "user",
) -> UserRoleHttpResponse:
    try:
        response = await use_case.execute(
            AssignActorRoleRequest(
                actor_id=actor_id,
                role_id=role_id,
                identity_type=identity_type,
                audit_context=audit_context,
            )
        )
    except RbacValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RbacNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except RbacConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return UserRoleHttpResponse.from_application(response)


@router.delete(
    "/actors/{actor_id}/roles/{role_id}",
    response_model=UserRoleHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid role assignment data."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "Role revoke permission is required."},
        status.HTTP_404_NOT_FOUND: {"description": "Actor or assignment not found."},
    },
    dependencies=[Depends(permission_required("role.revoke", "global"))],
)
async def revoke_actor_role(
    actor_id: str,
    role_id: str,
    use_case: RevokeActorRoleUseCaseDependency,
    audit_context: AuditContextDependency,
    identity_type: str = "user",
) -> UserRoleHttpResponse:
    try:
        response = await use_case.execute(
            RevokeActorRoleRequest(
                actor_id=actor_id,
                role_id=role_id,
                identity_type=identity_type,
                audit_context=audit_context,
            )
        )
    except RbacValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except RbacNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return UserRoleHttpResponse.from_application(response)

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from application.audit.dto import AuditContext
from application.project.dto import CreateProjectRequest, ListProjectsRequest
from application.project.exceptions import (
    ProjectAlreadyExistsError,
    ProjectValidationError,
    VaultNotFoundError,
)
from application.project.use_cases import CreateProjectUseCase, ListProjectsUseCase
from application.rbac.dto import RequirePermission
from application.rbac.exceptions import AuthorizationDeniedError, RbacValidationError
from application.rbac.use_cases import AuthorizeUseCase
from application.vault.dto import (
    ArchiveVaultRequest,
    CreateVaultRequest,
    GetVaultRequest,
    ListVaultsRequest,
    UpdateVaultRequest,
)
from application.vault.exceptions import (
    VaultAlreadyExistsError,
    VaultArchivedError,
    VaultValidationError,
)
from application.vault.exceptions import (
    VaultNotFoundError as ApplicationVaultNotFoundError,
)
from application.vault.use_cases import (
    ArchiveVaultUseCase,
    CreateVaultUseCase,
    GetVaultUseCase,
    ListVaultsUseCase,
    UpdateVaultUseCase,
)
from presentation.rest.audit_context import get_audit_context
from presentation.rest.authentication import AuthenticatedIdentity, get_authenticated_identity
from presentation.rest.authorization import permission_required
from presentation.rest.dependencies import (
    get_archive_vault_use_case,
    get_authorize_use_case,
    get_create_project_use_case,
    get_create_vault_use_case,
    get_list_projects_use_case,
    get_list_vaults_use_case,
    get_update_vault_use_case,
    get_vault_use_case,
)
from presentation.rest.schemas import (
    CreateProjectHttpRequest,
    CreateVaultHttpRequest,
    ProjectHttpResponse,
    ProjectListHttpResponse,
    UpdateVaultHttpRequest,
    VaultHttpResponse,
    VaultListHttpResponse,
)

router = APIRouter(prefix="/v1/vaults", tags=["vaults"])

CreateVaultUseCaseDependency = Annotated[
    CreateVaultUseCase,
    Depends(get_create_vault_use_case),
]
ListVaultsUseCaseDependency = Annotated[
    ListVaultsUseCase,
    Depends(get_list_vaults_use_case),
]
GetVaultUseCaseDependency = Annotated[
    GetVaultUseCase,
    Depends(get_vault_use_case),
]
UpdateVaultUseCaseDependency = Annotated[
    UpdateVaultUseCase,
    Depends(get_update_vault_use_case),
]
ArchiveVaultUseCaseDependency = Annotated[
    ArchiveVaultUseCase,
    Depends(get_archive_vault_use_case),
]
CreateProjectUseCaseDependency = Annotated[
    CreateProjectUseCase,
    Depends(get_create_project_use_case),
]
ListProjectsUseCaseDependency = Annotated[
    ListProjectsUseCase,
    Depends(get_list_projects_use_case),
]
AuditContextDependency = Annotated[AuditContext, Depends(get_audit_context)]
AuthenticatedIdentityDependency = Annotated[
    AuthenticatedIdentity,
    Depends(get_authenticated_identity),
]
AuthorizeUseCaseDependency = Annotated[
    AuthorizeUseCase,
    Depends(get_authorize_use_case),
]


async def authorize_vault_scope(
    permission: str,
    vault_id: str,
    identity: AuthenticatedIdentity,
    authorize_use_case: AuthorizeUseCase,
    request: Request,
) -> None:
    try:
        await authorize_use_case.execute(
            RequirePermission(
                identity_id=identity.id,
                identity_type=identity.type,
                permission=permission,
                scope_type="vault",
                scope_id=vault_id,
                ip_address=request.client.host if request.client is not None else None,
                user_agent=request.headers.get("User-Agent"),
                request_id=getattr(request.state, "request_id", None),
            )
        )
    except RbacValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except AuthorizationDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


@router.get(
    "",
    response_model=VaultListHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid vault list filters."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "Vault read permission is required."},
    },
    dependencies=[Depends(permission_required("vault.read", "global"))],
)
async def list_vaults(
    use_case: ListVaultsUseCaseDependency,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
    search: str | None = None,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    archived: bool | None = None,
    locked: bool | None = None,
) -> VaultListHttpResponse:
    try:
        response = await use_case.execute(
            ListVaultsRequest(
                page=page,
                page_size=page_size,
                search=search,
                status=status_filter,
                archived=archived,
                locked=locked,
            )
        )
    except VaultValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return VaultListHttpResponse.from_application(response)


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=VaultHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid vault data."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "Vault create permission is required."},
        status.HTTP_409_CONFLICT: {"description": "Vault name already exists."},
    },
    dependencies=[Depends(permission_required("vault.create", "global"))],
)
async def create_vault(
    payload: CreateVaultHttpRequest,
    use_case: CreateVaultUseCaseDependency,
    audit_context: AuditContextDependency,
) -> VaultHttpResponse:
    try:
        response = await use_case.execute(
            CreateVaultRequest(
                name=payload.name,
                description=payload.description,
                audit_context=audit_context,
            )
        )
    except VaultValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except VaultAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return VaultHttpResponse.from_application(response)


@router.get(
    "/{vault_id}",
    response_model=VaultHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid vault id."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "Vault read permission is required."},
        status.HTTP_404_NOT_FOUND: {"description": "Vault not found."},
    },
)
async def get_vault(
    vault_id: str,
    use_case: GetVaultUseCaseDependency,
    audit_context: AuditContextDependency,
    identity: AuthenticatedIdentityDependency,
    authorize_use_case: AuthorizeUseCaseDependency,
    request: Request,
) -> VaultHttpResponse:
    await authorize_vault_scope("vault.read", vault_id, identity, authorize_use_case, request)
    try:
        response = await use_case.execute(
            GetVaultRequest(vault_id=vault_id, audit_context=audit_context)
        )
    except VaultValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ApplicationVaultNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return VaultHttpResponse.from_application(response)


@router.patch(
    "/{vault_id}",
    response_model=VaultHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid vault data."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "Vault update permission is required."},
        status.HTTP_404_NOT_FOUND: {"description": "Vault not found."},
        status.HTTP_409_CONFLICT: {"description": "Vault name already exists or is archived."},
    },
)
async def update_vault(
    vault_id: str,
    payload: UpdateVaultHttpRequest,
    use_case: UpdateVaultUseCaseDependency,
    audit_context: AuditContextDependency,
    identity: AuthenticatedIdentityDependency,
    authorize_use_case: AuthorizeUseCaseDependency,
    request: Request,
) -> VaultHttpResponse:
    await authorize_vault_scope("vault.update", vault_id, identity, authorize_use_case, request)
    try:
        response = await use_case.execute(
            UpdateVaultRequest(
                vault_id=vault_id,
                name=payload.name,
                description=payload.description,
                audit_context=audit_context,
            )
        )
    except VaultValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ApplicationVaultNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (VaultAlreadyExistsError, VaultArchivedError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return VaultHttpResponse.from_application(response)


@router.post(
    "/{vault_id}/archive",
    response_model=VaultHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid vault id."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "Vault archive permission is required."},
        status.HTTP_404_NOT_FOUND: {"description": "Vault not found."},
    },
)
async def archive_vault(
    vault_id: str,
    use_case: ArchiveVaultUseCaseDependency,
    audit_context: AuditContextDependency,
    identity: AuthenticatedIdentityDependency,
    authorize_use_case: AuthorizeUseCaseDependency,
    request: Request,
) -> VaultHttpResponse:
    await authorize_vault_scope("vault.archive", vault_id, identity, authorize_use_case, request)
    try:
        response = await use_case.execute(
            ArchiveVaultRequest(vault_id=vault_id, audit_context=audit_context)
        )
    except VaultValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ApplicationVaultNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return VaultHttpResponse.from_application(response)


@router.post(
    "/{vault_id}/projects",
    status_code=status.HTTP_201_CREATED,
    response_model=ProjectHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid project data."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "Project create permission is required."},
        status.HTTP_404_NOT_FOUND: {"description": "Vault not found."},
        status.HTTP_409_CONFLICT: {"description": "Project name already exists in vault."},
    },
)
async def create_project(
    vault_id: str,
    payload: CreateProjectHttpRequest,
    use_case: CreateProjectUseCaseDependency,
    audit_context: AuditContextDependency,
    identity: AuthenticatedIdentityDependency,
    authorize_use_case: AuthorizeUseCaseDependency,
    request: Request,
) -> ProjectHttpResponse:
    await authorize_vault_scope("project.create", vault_id, identity, authorize_use_case, request)
    try:
        response = await use_case.execute(
            CreateProjectRequest(
                vault_id=vault_id,
                name=payload.name,
                description=payload.description,
                audit_context=audit_context,
            )
        )
    except ProjectValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except VaultNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ProjectAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return ProjectHttpResponse.from_application(response)


@router.get(
    "/{vault_id}/projects",
    response_model=ProjectListHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid project list filters."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "Project read permission is required."},
        status.HTTP_404_NOT_FOUND: {"description": "Vault not found."},
    },
)
async def list_projects(
    vault_id: str,
    use_case: ListProjectsUseCaseDependency,
    identity: AuthenticatedIdentityDependency,
    authorize_use_case: AuthorizeUseCaseDependency,
    request: Request,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
    search: str | None = None,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    archived: bool | None = None,
) -> ProjectListHttpResponse:
    await authorize_vault_scope("project.read", vault_id, identity, authorize_use_case, request)
    try:
        response = await use_case.execute(
            ListProjectsRequest(
                vault_id=vault_id,
                page=page,
                page_size=page_size,
                search=search,
                status=status_filter,
                archived=archived,
            )
        )
    except ProjectValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except VaultNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return ProjectListHttpResponse.from_application(response)

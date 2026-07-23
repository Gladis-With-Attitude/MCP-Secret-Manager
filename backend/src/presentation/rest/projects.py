from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status

from application.audit.dto import AuditContext
from application.project.dto import ArchiveProjectRequest, GetProjectRequest, UpdateProjectRequest
from application.project.exceptions import (
    ProjectAlreadyExistsError,
    ProjectArchivedError,
    ProjectNotFoundError,
    ProjectValidationError,
)
from application.project.use_cases import (
    ArchiveProjectUseCase,
    GetProjectUseCase,
    UpdateProjectUseCase,
)
from application.rbac.dto import RequirePermission
from application.rbac.exceptions import AuthorizationDeniedError, RbacValidationError
from application.rbac.use_cases import AuthorizeUseCase
from application.secret.dto import CreateSecretRequest, ListSecretsRequest
from application.secret.exceptions import (
    ProjectArchivedError as SecretProjectArchivedError,
)
from application.secret.exceptions import (
    ProjectNotFoundError as SecretProjectNotFoundError,
)
from application.secret.exceptions import (
    SecretAlreadyExistsError,
    SecretValidationError,
)
from application.secret.use_cases import CreateSecretUseCase, ListSecretsUseCase
from presentation.rest.audit_context import get_audit_context
from presentation.rest.authentication import AuthenticatedIdentity, get_authenticated_identity
from presentation.rest.dependencies import (
    get_archive_project_use_case,
    get_authorize_use_case,
    get_create_secret_use_case,
    get_list_secrets_use_case,
    get_project_use_case,
    get_update_project_use_case,
)
from presentation.rest.schemas import (
    CreateSecretHttpRequest,
    ProjectHttpResponse,
    SecretHttpResponse,
    SecretListHttpResponse,
    UpdateProjectHttpRequest,
)

router = APIRouter(prefix="/v1/projects", tags=["projects"])

CreateSecretUseCaseDependency = Annotated[
    CreateSecretUseCase,
    Depends(get_create_secret_use_case),
]
ListSecretsUseCaseDependency = Annotated[
    ListSecretsUseCase,
    Depends(get_list_secrets_use_case),
]
GetProjectUseCaseDependency = Annotated[
    GetProjectUseCase,
    Depends(get_project_use_case),
]
UpdateProjectUseCaseDependency = Annotated[
    UpdateProjectUseCase,
    Depends(get_update_project_use_case),
]
ArchiveProjectUseCaseDependency = Annotated[
    ArchiveProjectUseCase,
    Depends(get_archive_project_use_case),
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


async def authorize_project_scope(
    permission: str,
    project_id: str,
    identity: AuthenticatedIdentity,
    authorize_use_case: AuthorizeUseCase,
    request: Request,
    parent_vault_id: str | None = None,
) -> None:
    try:
        await authorize_use_case.execute(
            RequirePermission(
                identity_id=identity.id,
                identity_type=identity.type,
                permission=permission,
                scope_type="project",
                scope_id=project_id,
                parent_vault_id=parent_vault_id,
                ip_address=request.client.host if request.client is not None else None,
                user_agent=request.headers.get("User-Agent"),
                request_id=getattr(request.state, "request_id", None),
            )
        )
    except RbacValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except AuthorizationDeniedError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


async def resolve_project_for_authorization(
    project_id: str,
    use_case: GetProjectUseCase,
    audit_context: AuditContext | None,
) -> ProjectHttpResponse:
    try:
        response = await use_case.execute(
            GetProjectRequest(project_id=project_id, audit_context=audit_context)
        )
    except ProjectValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ProjectNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return ProjectHttpResponse.from_application(response)


@router.get(
    "/{project_id}",
    response_model=ProjectHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid project id."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "Project read permission is required."},
        status.HTTP_404_NOT_FOUND: {"description": "Project not found."},
    },
)
async def get_project(
    project_id: str,
    use_case: GetProjectUseCaseDependency,
    audit_context: AuditContextDependency,
    identity: AuthenticatedIdentityDependency,
    authorize_use_case: AuthorizeUseCaseDependency,
    request: Request,
) -> ProjectHttpResponse:
    response = await resolve_project_for_authorization(project_id, use_case, audit_context)
    await authorize_project_scope(
        "project.read",
        project_id,
        identity,
        authorize_use_case,
        request,
        parent_vault_id=response.vault_id,
    )
    return response


@router.patch(
    "/{project_id}",
    response_model=ProjectHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid project data."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "Project update permission is required."},
        status.HTTP_404_NOT_FOUND: {"description": "Project not found."},
        status.HTTP_409_CONFLICT: {"description": "Project name already exists or is archived."},
    },
)
async def update_project(
    project_id: str,
    payload: UpdateProjectHttpRequest,
    use_case: UpdateProjectUseCaseDependency,
    get_project_use_case: GetProjectUseCaseDependency,
    audit_context: AuditContextDependency,
    identity: AuthenticatedIdentityDependency,
    authorize_use_case: AuthorizeUseCaseDependency,
    request: Request,
) -> ProjectHttpResponse:
    project = await resolve_project_for_authorization(
        project_id,
        get_project_use_case,
        audit_context,
    )
    await authorize_project_scope(
        "project.update",
        project_id,
        identity,
        authorize_use_case,
        request,
        parent_vault_id=project.vault_id,
    )
    try:
        response = await use_case.execute(
            UpdateProjectRequest(
                project_id=project_id,
                name=payload.name,
                description=payload.description,
                audit_context=audit_context,
            )
        )
    except ProjectValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ProjectNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (ProjectAlreadyExistsError, ProjectArchivedError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return ProjectHttpResponse.from_application(response)


@router.post(
    "/{project_id}/archive",
    response_model=ProjectHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid project id."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "Project archive permission is required."},
        status.HTTP_404_NOT_FOUND: {"description": "Project not found."},
    },
)
async def archive_project(
    project_id: str,
    use_case: ArchiveProjectUseCaseDependency,
    get_project_use_case: GetProjectUseCaseDependency,
    audit_context: AuditContextDependency,
    identity: AuthenticatedIdentityDependency,
    authorize_use_case: AuthorizeUseCaseDependency,
    request: Request,
) -> ProjectHttpResponse:
    project = await resolve_project_for_authorization(
        project_id,
        get_project_use_case,
        audit_context,
    )
    await authorize_project_scope(
        "project.archive",
        project_id,
        identity,
        authorize_use_case,
        request,
        parent_vault_id=project.vault_id,
    )
    try:
        response = await use_case.execute(
            ArchiveProjectRequest(project_id=project_id, audit_context=audit_context)
        )
    except ProjectValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ProjectNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return ProjectHttpResponse.from_application(response)


@router.post(
    "/{project_id}/secrets",
    status_code=status.HTTP_201_CREATED,
    response_model=SecretHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid secret data."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "Secret create permission is required."},
        status.HTTP_404_NOT_FOUND: {"description": "Project not found."},
        status.HTTP_409_CONFLICT: {"description": "Secret key already exists in project."},
    },
)
async def create_secret(
    project_id: str,
    payload: CreateSecretHttpRequest,
    use_case: CreateSecretUseCaseDependency,
    get_project_use_case: GetProjectUseCaseDependency,
    audit_context: AuditContextDependency,
    identity: AuthenticatedIdentityDependency,
    authorize_use_case: AuthorizeUseCaseDependency,
    request: Request,
) -> SecretHttpResponse:
    project = await resolve_project_for_authorization(
        project_id,
        get_project_use_case,
        audit_context,
    )
    await authorize_project_scope(
        "secret.create",
        project_id,
        identity,
        authorize_use_case,
        request,
        parent_vault_id=project.vault_id,
    )
    try:
        response = await use_case.execute(
            CreateSecretRequest(
                project_id=project_id,
                key=payload.key,
                description=payload.description,
                type=payload.type,
                metadata=payload.metadata,
                tags=tuple(payload.tags),
                audit_context=audit_context,
            )
        )
    except SecretValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except SecretProjectNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except SecretProjectArchivedError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except SecretAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return SecretHttpResponse.from_application(response)


@router.get(
    "/{project_id}/secrets",
    response_model=SecretListHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid secret list filters."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "Secret read permission is required."},
        status.HTTP_404_NOT_FOUND: {"description": "Project not found."},
    },
)
async def list_secrets(
    project_id: str,
    use_case: ListSecretsUseCaseDependency,
    get_project_use_case: GetProjectUseCaseDependency,
    audit_context: AuditContextDependency,
    identity: AuthenticatedIdentityDependency,
    authorize_use_case: AuthorizeUseCaseDependency,
    request: Request,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
    search: str | None = None,
    q: str | None = None,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    archived: bool | None = None,
    type_filter: Annotated[str | None, Query(alias="type")] = None,
) -> SecretListHttpResponse:
    project = await resolve_project_for_authorization(
        project_id,
        get_project_use_case,
        audit_context,
    )
    await authorize_project_scope(
        "secret.read",
        project_id,
        identity,
        authorize_use_case,
        request,
        parent_vault_id=project.vault_id,
    )
    try:
        response = await use_case.execute(
            ListSecretsRequest(
                project_id=project_id,
                page=page,
                page_size=page_size,
                search=search or q,
                status=status_filter,
                archived=archived,
                type=type_filter,
                audit_context=audit_context,
            )
        )
    except SecretValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except SecretProjectNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return SecretListHttpResponse.from_application(response)

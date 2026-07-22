from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

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
from presentation.rest.dependencies import (
    get_archive_project_use_case,
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


@router.get(
    "/{project_id}",
    response_model=ProjectHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid project id."},
        status.HTTP_404_NOT_FOUND: {"description": "Project not found."},
    },
)
async def get_project(
    project_id: str,
    use_case: GetProjectUseCaseDependency,
    audit_context: AuditContextDependency,
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


@router.patch(
    "/{project_id}",
    response_model=ProjectHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid project data."},
        status.HTTP_404_NOT_FOUND: {"description": "Project not found."},
        status.HTTP_409_CONFLICT: {"description": "Project name already exists or is archived."},
    },
)
async def update_project(
    project_id: str,
    payload: UpdateProjectHttpRequest,
    use_case: UpdateProjectUseCaseDependency,
    audit_context: AuditContextDependency,
) -> ProjectHttpResponse:
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
        status.HTTP_404_NOT_FOUND: {"description": "Project not found."},
    },
)
async def archive_project(
    project_id: str,
    use_case: ArchiveProjectUseCaseDependency,
    audit_context: AuditContextDependency,
) -> ProjectHttpResponse:
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
        status.HTTP_404_NOT_FOUND: {"description": "Project not found."},
        status.HTTP_409_CONFLICT: {"description": "Secret key already exists in project."},
    },
)
async def create_secret(
    project_id: str,
    payload: CreateSecretHttpRequest,
    use_case: CreateSecretUseCaseDependency,
    audit_context: AuditContextDependency,
) -> SecretHttpResponse:
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
        status.HTTP_404_NOT_FOUND: {"description": "Project not found."},
    },
)
async def list_secrets(
    project_id: str,
    use_case: ListSecretsUseCaseDependency,
    audit_context: AuditContextDependency,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
    search: str | None = None,
    q: str | None = None,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
    archived: bool | None = None,
    type_filter: Annotated[str | None, Query(alias="type")] = None,
) -> SecretListHttpResponse:
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

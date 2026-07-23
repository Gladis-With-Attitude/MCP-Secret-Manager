from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from application.audit.dto import AuditContext
from application.project.dto import GetProjectRequest
from application.project.exceptions import (
    ProjectNotFoundError,
    ProjectValidationError,
)
from application.project.use_cases import GetProjectUseCase
from application.rbac.dto import RequirePermission
from application.rbac.exceptions import AuthorizationDeniedError, RbacValidationError
from application.rbac.use_cases import AuthorizeUseCase
from application.secret.dto import ArchiveSecretRequest, GetSecretRequest, UpdateSecretRequest
from application.secret.exceptions import (
    SecretAlreadyExistsError,
    SecretArchivedError,
    SecretValidationError,
)
from application.secret.exceptions import (
    SecretNotFoundError as SecretMetadataNotFoundError,
)
from application.secret.use_cases import ArchiveSecretUseCase, GetSecretUseCase, UpdateSecretUseCase
from application.secret_version.dto import CreateSecretVersionRequest, RestoreSecretVersionRequest
from application.secret_version.exceptions import (
    SecretNotFoundError,
    SecretVersionConflictError,
    SecretVersionCryptoError,
    SecretVersionNotFoundError,
    SecretVersionValidationError,
)
from application.secret_version.use_cases import (
    CreateSecretVersionUseCase,
    GetActiveSecretVersionUseCase,
    GetSecretVersionMetadataUseCase,
    ListSecretVersionsUseCase,
    RestoreSecretVersionUseCase,
)
from presentation.rest.audit_context import get_audit_context
from presentation.rest.authentication import AuthenticatedIdentity, get_authenticated_identity
from presentation.rest.dependencies import (
    get_active_secret_version_use_case,
    get_archive_secret_use_case,
    get_authorize_use_case,
    get_create_secret_version_use_case,
    get_list_secret_versions_use_case,
    get_project_use_case,
    get_restore_secret_version_use_case,
    get_secret_use_case,
    get_secret_version_metadata_use_case,
    get_update_secret_use_case,
)
from presentation.rest.schemas import (
    CreateSecretVersionHttpRequest,
    SecretHttpResponse,
    SecretVersionMetadataHttpResponse,
    SecretVersionValueHttpResponse,
    UpdateSecretHttpRequest,
)

router = APIRouter(prefix="/v1/secrets", tags=["secrets"])

CreateSecretVersionUseCaseDependency = Annotated[
    CreateSecretVersionUseCase,
    Depends(get_create_secret_version_use_case),
]
ListSecretVersionsUseCaseDependency = Annotated[
    ListSecretVersionsUseCase,
    Depends(get_list_secret_versions_use_case),
]
GetSecretVersionMetadataUseCaseDependency = Annotated[
    GetSecretVersionMetadataUseCase,
    Depends(get_secret_version_metadata_use_case),
]
GetActiveSecretVersionUseCaseDependency = Annotated[
    GetActiveSecretVersionUseCase,
    Depends(get_active_secret_version_use_case),
]
RestoreSecretVersionUseCaseDependency = Annotated[
    RestoreSecretVersionUseCase,
    Depends(get_restore_secret_version_use_case),
]
GetSecretUseCaseDependency = Annotated[
    GetSecretUseCase,
    Depends(get_secret_use_case),
]
UpdateSecretUseCaseDependency = Annotated[
    UpdateSecretUseCase,
    Depends(get_update_secret_use_case),
]
ArchiveSecretUseCaseDependency = Annotated[
    ArchiveSecretUseCase,
    Depends(get_archive_secret_use_case),
]
GetProjectUseCaseDependency = Annotated[
    GetProjectUseCase,
    Depends(get_project_use_case),
]
AuditContextDependency = Annotated[AuditContext, Depends(get_audit_context)]
AuthenticatedIdentityDependency = Annotated[
    AuthenticatedIdentity,
    Depends(get_authenticated_identity),
]
AuthorizeUseCaseDependency = Annotated[AuthorizeUseCase, Depends(get_authorize_use_case)]


async def authorize_secret_scope(
    permission: str,
    secret_id: str,
    parent_project_id: str,
    parent_vault_id: str,
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
                scope_type="secret",
                scope_id=secret_id,
                parent_project_id=parent_project_id,
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


async def resolve_secret_for_authorization(
    secret_id: str,
    get_secret_use_case: GetSecretUseCase,
    get_project_use_case: GetProjectUseCase,
    audit_context: AuditContext | None,
) -> tuple[SecretHttpResponse, str]:
    try:
        secret = await get_secret_use_case.execute(
            GetSecretRequest(secret_id=secret_id, audit_context=audit_context)
        )
        project = await get_project_use_case.execute(
            GetProjectRequest(project_id=secret.project_id, audit_context=audit_context)
        )
    except SecretValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ProjectValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except (SecretMetadataNotFoundError, ProjectNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return SecretHttpResponse.from_application(secret), project.vault_id


async def authorize_existing_secret(
    permission: str,
    secret_id: str,
    get_secret_use_case: GetSecretUseCase,
    get_project_use_case: GetProjectUseCase,
    audit_context: AuditContext | None,
    identity: AuthenticatedIdentity,
    authorize_use_case: AuthorizeUseCase,
    request: Request,
) -> SecretHttpResponse:
    secret, parent_vault_id = await resolve_secret_for_authorization(
        secret_id,
        get_secret_use_case,
        get_project_use_case,
        audit_context,
    )
    await authorize_secret_scope(
        permission,
        secret_id,
        secret.project_id,
        parent_vault_id,
        identity,
        authorize_use_case,
        request,
    )
    return secret


@router.get(
    "/{secret_id}",
    response_model=SecretHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid secret id."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "Secret read permission is required."},
        status.HTTP_404_NOT_FOUND: {"description": "Secret not found."},
    },
)
async def get_secret(
    secret_id: str,
    use_case: GetSecretUseCaseDependency,
    get_project_use_case: GetProjectUseCaseDependency,
    audit_context: AuditContextDependency,
    identity: AuthenticatedIdentityDependency,
    authorize_use_case: AuthorizeUseCaseDependency,
    request: Request,
) -> SecretHttpResponse:
    secret = await authorize_existing_secret(
        "secret.read",
        secret_id,
        use_case,
        get_project_use_case,
        audit_context,
        identity,
        authorize_use_case,
        request,
    )
    return secret


@router.patch(
    "/{secret_id}",
    response_model=SecretHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid secret metadata."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "Secret update permission is required."},
        status.HTTP_404_NOT_FOUND: {"description": "Secret not found."},
        status.HTTP_409_CONFLICT: {"description": "Secret key already exists or is archived."},
    },
)
async def update_secret(
    secret_id: str,
    payload: UpdateSecretHttpRequest,
    use_case: UpdateSecretUseCaseDependency,
    get_secret_use_case: GetSecretUseCaseDependency,
    get_project_use_case: GetProjectUseCaseDependency,
    audit_context: AuditContextDependency,
    identity: AuthenticatedIdentityDependency,
    authorize_use_case: AuthorizeUseCaseDependency,
    request: Request,
) -> SecretHttpResponse:
    await authorize_existing_secret(
        "secret.update",
        secret_id,
        get_secret_use_case,
        get_project_use_case,
        audit_context,
        identity,
        authorize_use_case,
        request,
    )
    try:
        response = await use_case.execute(
            UpdateSecretRequest(
                secret_id=secret_id,
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
    except SecretMetadataNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except (SecretAlreadyExistsError, SecretArchivedError) as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return SecretHttpResponse.from_application(response)


@router.post(
    "/{secret_id}/archive",
    response_model=SecretHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid secret id."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "Secret archive permission is required."},
        status.HTTP_404_NOT_FOUND: {"description": "Secret not found."},
    },
)
async def archive_secret(
    secret_id: str,
    use_case: ArchiveSecretUseCaseDependency,
    get_secret_use_case: GetSecretUseCaseDependency,
    get_project_use_case: GetProjectUseCaseDependency,
    audit_context: AuditContextDependency,
    identity: AuthenticatedIdentityDependency,
    authorize_use_case: AuthorizeUseCaseDependency,
    request: Request,
) -> SecretHttpResponse:
    await authorize_existing_secret(
        "secret.archive",
        secret_id,
        get_secret_use_case,
        get_project_use_case,
        audit_context,
        identity,
        authorize_use_case,
        request,
    )
    try:
        response = await use_case.execute(
            ArchiveSecretRequest(secret_id=secret_id, audit_context=audit_context)
        )
    except SecretValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except SecretMetadataNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return SecretHttpResponse.from_application(response)


@router.post(
    "/{secret_id}/versions",
    status_code=status.HTTP_201_CREATED,
    response_model=SecretVersionMetadataHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid secret version data."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "Secret rotate permission is required."},
        status.HTTP_404_NOT_FOUND: {"description": "Secret not found."},
        status.HTTP_409_CONFLICT: {"description": "Secret version conflict."},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Secret version crypto failure."},
    },
)
async def create_secret_version(
    secret_id: str,
    payload: CreateSecretVersionHttpRequest,
    use_case: CreateSecretVersionUseCaseDependency,
    get_secret_use_case: GetSecretUseCaseDependency,
    get_project_use_case: GetProjectUseCaseDependency,
    audit_context: AuditContextDependency,
    identity: AuthenticatedIdentityDependency,
    authorize_use_case: AuthorizeUseCaseDependency,
    request: Request,
) -> SecretVersionMetadataHttpResponse:
    secret = await authorize_existing_secret(
        "secret.rotate",
        secret_id,
        get_secret_use_case,
        get_project_use_case,
        audit_context,
        identity,
        authorize_use_case,
        request,
    )
    try:
        response = await use_case.execute(
            CreateSecretVersionRequest(
                secret_id=secret_id,
                value=payload.value,
                project_id=secret.project_id,
                audit_context=audit_context,
            )
        )
    except SecretVersionValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except SecretNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except SecretVersionConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except SecretVersionCryptoError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Secret version cryptographic operation failed.",
        ) from exc

    return SecretVersionMetadataHttpResponse.from_application(response)


@router.get(
    "/{secret_id}/versions",
    response_model=list[SecretVersionMetadataHttpResponse],
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid secret id."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "Secret read permission is required."},
        status.HTTP_404_NOT_FOUND: {"description": "Secret not found."},
    },
)
async def list_secret_versions(
    secret_id: str,
    use_case: ListSecretVersionsUseCaseDependency,
    get_secret_use_case: GetSecretUseCaseDependency,
    get_project_use_case: GetProjectUseCaseDependency,
    audit_context: AuditContextDependency,
    identity: AuthenticatedIdentityDependency,
    authorize_use_case: AuthorizeUseCaseDependency,
    request: Request,
) -> list[SecretVersionMetadataHttpResponse]:
    secret = await authorize_existing_secret(
        "secret.read",
        secret_id,
        get_secret_use_case,
        get_project_use_case,
        audit_context,
        identity,
        authorize_use_case,
        request,
    )
    try:
        response = await use_case.execute(
            secret_id,
            audit_context=audit_context,
            project_id=secret.project_id,
        )
    except SecretVersionValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except SecretNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return [SecretVersionMetadataHttpResponse.from_application(item) for item in response]


@router.get(
    "/{secret_id}/versions/latest",
    response_model=SecretVersionValueHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid secret id."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "Secret decrypt permission is required."},
        status.HTTP_404_NOT_FOUND: {"description": "Secret or active version not found."},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Secret version crypto failure."},
    },
)
async def get_latest_secret_version(
    secret_id: str,
    use_case: GetActiveSecretVersionUseCaseDependency,
    get_secret_use_case: GetSecretUseCaseDependency,
    get_project_use_case: GetProjectUseCaseDependency,
    audit_context: AuditContextDependency,
    identity: AuthenticatedIdentityDependency,
    authorize_use_case: AuthorizeUseCaseDependency,
    request: Request,
) -> SecretVersionValueHttpResponse:
    secret = await authorize_existing_secret(
        "secret.decrypt",
        secret_id,
        get_secret_use_case,
        get_project_use_case,
        audit_context,
        identity,
        authorize_use_case,
        request,
    )
    try:
        response = await use_case.execute(
            secret_id,
            audit_context=audit_context,
            project_id=secret.project_id,
        )
    except SecretVersionValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except (SecretNotFoundError, SecretVersionNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except SecretVersionCryptoError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Secret version cryptographic operation failed.",
        ) from exc

    return SecretVersionValueHttpResponse.from_application(response)


@router.get(
    "/{secret_id}/versions/{version_id}",
    response_model=SecretVersionMetadataHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid secret or version id."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "Secret read permission is required."},
        status.HTTP_404_NOT_FOUND: {"description": "Secret or version not found."},
    },
)
async def get_secret_version(
    secret_id: str,
    version_id: str,
    use_case: GetSecretVersionMetadataUseCaseDependency,
    get_secret_use_case: GetSecretUseCaseDependency,
    get_project_use_case: GetProjectUseCaseDependency,
    audit_context: AuditContextDependency,
    identity: AuthenticatedIdentityDependency,
    authorize_use_case: AuthorizeUseCaseDependency,
    request: Request,
) -> SecretVersionMetadataHttpResponse:
    secret = await authorize_existing_secret(
        "secret.read",
        secret_id,
        get_secret_use_case,
        get_project_use_case,
        audit_context,
        identity,
        authorize_use_case,
        request,
    )
    try:
        response = await use_case.execute(
            secret_id,
            version_id,
            audit_context=audit_context,
            project_id=secret.project_id,
        )
    except SecretVersionValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except (SecretNotFoundError, SecretVersionNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return SecretVersionMetadataHttpResponse.from_application(response)


@router.post(
    "/{secret_id}/versions/{version_id}/restore",
    response_model=SecretVersionMetadataHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid secret or version id."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "Secret rotate permission is required."},
        status.HTTP_404_NOT_FOUND: {"description": "Secret or version not found."},
        status.HTTP_409_CONFLICT: {"description": "Secret version conflict."},
    },
)
async def restore_secret_version(
    secret_id: str,
    version_id: str,
    use_case: RestoreSecretVersionUseCaseDependency,
    get_secret_use_case: GetSecretUseCaseDependency,
    get_project_use_case: GetProjectUseCaseDependency,
    audit_context: AuditContextDependency,
    identity: AuthenticatedIdentityDependency,
    authorize_use_case: AuthorizeUseCaseDependency,
    request: Request,
) -> SecretVersionMetadataHttpResponse:
    secret = await authorize_existing_secret(
        "secret.rotate",
        secret_id,
        get_secret_use_case,
        get_project_use_case,
        audit_context,
        identity,
        authorize_use_case,
        request,
    )
    try:
        response = await use_case.execute(
            RestoreSecretVersionRequest(
                secret_id=secret_id,
                version_id=version_id,
                project_id=secret.project_id,
                audit_context=audit_context,
            )
        )
    except SecretVersionValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except (SecretNotFoundError, SecretVersionNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except SecretVersionConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return SecretVersionMetadataHttpResponse.from_application(response)

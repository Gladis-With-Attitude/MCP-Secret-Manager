from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from application.audit.dto import AuditContext
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
from application.secret_version.dto import CreateSecretVersionRequest
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
    ListSecretVersionsUseCase,
)
from presentation.rest.audit_context import get_audit_context
from presentation.rest.dependencies import (
    get_active_secret_version_use_case,
    get_archive_secret_use_case,
    get_create_secret_version_use_case,
    get_list_secret_versions_use_case,
    get_secret_use_case,
    get_update_secret_use_case,
)
from presentation.rest.schemas import (
    CreateSecretVersionHttpRequest,
    SecretHttpResponse,
    SecretVersionHttpResponse,
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
GetActiveSecretVersionUseCaseDependency = Annotated[
    GetActiveSecretVersionUseCase,
    Depends(get_active_secret_version_use_case),
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
AuditContextDependency = Annotated[AuditContext, Depends(get_audit_context)]


@router.get(
    "/{secret_id}",
    response_model=SecretHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid secret id."},
        status.HTTP_404_NOT_FOUND: {"description": "Secret not found."},
    },
)
async def get_secret(
    secret_id: str,
    use_case: GetSecretUseCaseDependency,
    audit_context: AuditContextDependency,
) -> SecretHttpResponse:
    try:
        response = await use_case.execute(
            GetSecretRequest(secret_id=secret_id, audit_context=audit_context)
        )
    except SecretValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except SecretMetadataNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return SecretHttpResponse.from_application(response)


@router.patch(
    "/{secret_id}",
    response_model=SecretHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid secret metadata."},
        status.HTTP_404_NOT_FOUND: {"description": "Secret not found."},
        status.HTTP_409_CONFLICT: {"description": "Secret key already exists or is archived."},
    },
)
async def update_secret(
    secret_id: str,
    payload: UpdateSecretHttpRequest,
    use_case: UpdateSecretUseCaseDependency,
    audit_context: AuditContextDependency,
) -> SecretHttpResponse:
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
        status.HTTP_404_NOT_FOUND: {"description": "Secret not found."},
    },
)
async def archive_secret(
    secret_id: str,
    use_case: ArchiveSecretUseCaseDependency,
    audit_context: AuditContextDependency,
) -> SecretHttpResponse:
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
    response_model=SecretVersionHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid secret version data."},
        status.HTTP_404_NOT_FOUND: {"description": "Secret not found."},
        status.HTTP_409_CONFLICT: {"description": "Secret version conflict."},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Secret version crypto failure."},
    },
)
async def create_secret_version(
    secret_id: str,
    payload: CreateSecretVersionHttpRequest,
    use_case: CreateSecretVersionUseCaseDependency,
    audit_context: AuditContextDependency,
) -> SecretVersionHttpResponse:
    try:
        response = await use_case.execute(
            CreateSecretVersionRequest(
                secret_id=secret_id,
                value=payload.value,
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

    return SecretVersionHttpResponse.from_application(response)


@router.get(
    "/{secret_id}/versions",
    response_model=list[SecretVersionHttpResponse],
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid secret id."},
        status.HTTP_404_NOT_FOUND: {"description": "Secret not found."},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Secret version crypto failure."},
    },
)
async def list_secret_versions(
    secret_id: str,
    use_case: ListSecretVersionsUseCaseDependency,
    audit_context: AuditContextDependency,
) -> list[SecretVersionHttpResponse]:
    try:
        response = await use_case.execute(secret_id, audit_context=audit_context)
    except SecretVersionValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except SecretNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except SecretVersionCryptoError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Secret version cryptographic operation failed.",
        ) from exc

    return [SecretVersionHttpResponse.from_application(item) for item in response]


@router.get(
    "/{secret_id}/versions/latest",
    response_model=SecretVersionHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid secret id."},
        status.HTTP_404_NOT_FOUND: {"description": "Secret or active version not found."},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Secret version crypto failure."},
    },
)
async def get_latest_secret_version(
    secret_id: str,
    use_case: GetActiveSecretVersionUseCaseDependency,
    audit_context: AuditContextDependency,
) -> SecretVersionHttpResponse:
    try:
        response = await use_case.execute(secret_id, audit_context=audit_context)
    except SecretVersionValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except (SecretNotFoundError, SecretVersionNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except SecretVersionCryptoError as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Secret version cryptographic operation failed.",
        ) from exc

    return SecretVersionHttpResponse.from_application(response)

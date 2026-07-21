from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from application.secret_version.dto import CreateSecretVersionRequest
from application.secret_version.exceptions import (
    SecretNotFoundError,
    SecretVersionConflictError,
    SecretVersionNotFoundError,
    SecretVersionValidationError,
)
from application.secret_version.use_cases import (
    CreateSecretVersionUseCase,
    GetActiveSecretVersionUseCase,
    ListSecretVersionsUseCase,
)
from presentation.rest.dependencies import (
    get_active_secret_version_use_case,
    get_create_secret_version_use_case,
    get_list_secret_versions_use_case,
)
from presentation.rest.schemas import (
    CreateSecretVersionHttpRequest,
    SecretVersionHttpResponse,
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


@router.post(
    "/{secret_id}/versions",
    status_code=status.HTTP_201_CREATED,
    response_model=SecretVersionHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid secret version data."},
        status.HTTP_404_NOT_FOUND: {"description": "Secret not found."},
        status.HTTP_409_CONFLICT: {"description": "Secret version conflict."},
    },
)
async def create_secret_version(
    secret_id: str,
    payload: CreateSecretVersionHttpRequest,
    use_case: CreateSecretVersionUseCaseDependency,
) -> SecretVersionHttpResponse:
    try:
        response = await use_case.execute(
            CreateSecretVersionRequest(secret_id=secret_id, value=payload.value)
        )
    except SecretVersionValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except SecretNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except SecretVersionConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return SecretVersionHttpResponse.from_application(response)


@router.get(
    "/{secret_id}/versions",
    response_model=list[SecretVersionHttpResponse],
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid secret id."},
        status.HTTP_404_NOT_FOUND: {"description": "Secret not found."},
    },
)
async def list_secret_versions(
    secret_id: str,
    use_case: ListSecretVersionsUseCaseDependency,
) -> list[SecretVersionHttpResponse]:
    try:
        response = await use_case.execute(secret_id)
    except SecretVersionValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except SecretNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return [SecretVersionHttpResponse.from_application(item) for item in response]


@router.get(
    "/{secret_id}/versions/latest",
    response_model=SecretVersionHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid secret id."},
        status.HTTP_404_NOT_FOUND: {"description": "Secret or active version not found."},
    },
)
async def get_latest_secret_version(
    secret_id: str,
    use_case: GetActiveSecretVersionUseCaseDependency,
) -> SecretVersionHttpResponse:
    try:
        response = await use_case.execute(secret_id)
    except SecretVersionValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except (SecretNotFoundError, SecretVersionNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return SecretVersionHttpResponse.from_application(response)

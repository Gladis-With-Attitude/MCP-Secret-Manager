from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from application.secret.dto import CreateSecretRequest
from application.secret.exceptions import (
    ProjectNotFoundError,
    SecretAlreadyExistsError,
    SecretValidationError,
)
from application.secret.use_cases import CreateSecretUseCase
from presentation.rest.dependencies import get_create_secret_use_case
from presentation.rest.schemas import CreateSecretHttpRequest, SecretHttpResponse

router = APIRouter(prefix="/v1/projects", tags=["projects"])

CreateSecretUseCaseDependency = Annotated[
    CreateSecretUseCase,
    Depends(get_create_secret_use_case),
]


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
) -> SecretHttpResponse:
    try:
        response = await use_case.execute(
            CreateSecretRequest(
                project_id=project_id,
                key=payload.key,
                description=payload.description,
            )
        )
    except SecretValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except ProjectNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except SecretAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return SecretHttpResponse.from_application(response)

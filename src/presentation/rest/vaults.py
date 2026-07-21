from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from application.project.dto import CreateProjectRequest
from application.project.exceptions import (
    ProjectAlreadyExistsError,
    ProjectValidationError,
    VaultNotFoundError,
)
from application.project.use_cases import CreateProjectUseCase
from application.vault.dto import CreateVaultRequest
from application.vault.exceptions import VaultAlreadyExistsError, VaultValidationError
from application.vault.use_cases import CreateVaultUseCase
from presentation.rest.dependencies import get_create_project_use_case, get_create_vault_use_case
from presentation.rest.schemas import (
    CreateProjectHttpRequest,
    CreateVaultHttpRequest,
    ProjectHttpResponse,
    VaultHttpResponse,
)

router = APIRouter(prefix="/v1/vaults", tags=["vaults"])

CreateVaultUseCaseDependency = Annotated[
    CreateVaultUseCase,
    Depends(get_create_vault_use_case),
]
CreateProjectUseCaseDependency = Annotated[
    CreateProjectUseCase,
    Depends(get_create_project_use_case),
]


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=VaultHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid vault data."},
        status.HTTP_409_CONFLICT: {"description": "Vault name already exists."},
    },
)
async def create_vault(
    payload: CreateVaultHttpRequest,
    use_case: CreateVaultUseCaseDependency,
) -> VaultHttpResponse:
    try:
        response = await use_case.execute(CreateVaultRequest(name=payload.name))
    except VaultValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except VaultAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return VaultHttpResponse.from_application(response)


@router.post(
    "/{vault_id}/projects",
    status_code=status.HTTP_201_CREATED,
    response_model=ProjectHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid project data."},
        status.HTTP_404_NOT_FOUND: {"description": "Vault not found."},
        status.HTTP_409_CONFLICT: {"description": "Project name already exists in vault."},
    },
)
async def create_project(
    vault_id: str,
    payload: CreateProjectHttpRequest,
    use_case: CreateProjectUseCaseDependency,
) -> ProjectHttpResponse:
    try:
        response = await use_case.execute(
            CreateProjectRequest(vault_id=vault_id, name=payload.name)
        )
    except ProjectValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except VaultNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ProjectAlreadyExistsError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return ProjectHttpResponse.from_application(response)

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from application.audit.dto import AuditContext
from application.identity.dto import (
    CreateApiKeyRequest,
    CreateServiceAccountRequest,
    CreateUserRequest,
)
from application.identity.exceptions import (
    IdentityConflictError,
    IdentityNotFoundError,
    IdentityValidationError,
)
from application.identity.use_cases import (
    CreateApiKeyUseCase,
    CreateServiceAccountUseCase,
    CreateUserUseCase,
)
from presentation.rest.audit_context import get_audit_context
from presentation.rest.authentication import (
    AuthenticatedIdentity,
    get_optional_authenticated_identity,
)
from presentation.rest.dependencies import (
    get_create_api_key_use_case,
    get_create_service_account_use_case,
    get_create_user_use_case,
)
from presentation.rest.schemas import (
    ApiKeyCreatedHttpResponse,
    CreateApiKeyHttpRequest,
    CreateServiceAccountHttpRequest,
    CreateUserHttpRequest,
    ServiceAccountHttpResponse,
    UserHttpResponse,
)

router = APIRouter(prefix="/v1", tags=["identity"])

CreateUserUseCaseDependency = Annotated[CreateUserUseCase, Depends(get_create_user_use_case)]
CreateServiceAccountUseCaseDependency = Annotated[
    CreateServiceAccountUseCase,
    Depends(get_create_service_account_use_case),
]
CreateApiKeyUseCaseDependency = Annotated[
    CreateApiKeyUseCase,
    Depends(get_create_api_key_use_case),
]
OptionalIdentityDependency = Annotated[
    AuthenticatedIdentity | None,
    Depends(get_optional_authenticated_identity),
]
AuditContextDependency = Annotated[AuditContext, Depends(get_audit_context)]


@router.post(
    "/users",
    status_code=status.HTTP_201_CREATED,
    response_model=UserHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid user data."},
        status.HTTP_409_CONFLICT: {"description": "User already exists."},
    },
)
async def create_user(
    payload: CreateUserHttpRequest,
    use_case: CreateUserUseCaseDependency,
    audit_context: AuditContextDependency,
    _identity: OptionalIdentityDependency,
) -> UserHttpResponse:
    try:
        response = await use_case.execute(
            CreateUserRequest(
                email=payload.email,
                display_name=payload.display_name,
                audit_context=audit_context,
            )
        )
    except IdentityValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except IdentityConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return UserHttpResponse.from_application(response)


@router.post(
    "/service-accounts",
    status_code=status.HTTP_201_CREATED,
    response_model=ServiceAccountHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid service account data."},
        status.HTTP_404_NOT_FOUND: {"description": "Project not found."},
        status.HTTP_409_CONFLICT: {"description": "Service account already exists."},
    },
)
async def create_service_account(
    payload: CreateServiceAccountHttpRequest,
    use_case: CreateServiceAccountUseCaseDependency,
    audit_context: AuditContextDependency,
    _identity: OptionalIdentityDependency,
) -> ServiceAccountHttpResponse:
    try:
        response = await use_case.execute(
            CreateServiceAccountRequest(
                project_id=payload.project_id,
                name=payload.name,
                description=payload.description,
                audit_context=audit_context,
            )
        )
    except IdentityValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except IdentityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except IdentityConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return ServiceAccountHttpResponse.from_application(response)


@router.post(
    "/api-keys",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiKeyCreatedHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid API key data."},
        status.HTTP_404_NOT_FOUND: {"description": "Owner not found."},
        status.HTTP_409_CONFLICT: {"description": "API key conflict."},
    },
)
async def create_api_key(
    payload: CreateApiKeyHttpRequest,
    use_case: CreateApiKeyUseCaseDependency,
    audit_context: AuditContextDependency,
    _identity: OptionalIdentityDependency,
) -> ApiKeyCreatedHttpResponse:
    try:
        response = await use_case.execute(
            CreateApiKeyRequest(
                owner_id=payload.owner_id,
                owner_type=payload.owner_type,
                expires_at=payload.expires_at,
                audit_context=audit_context,
            )
        )
    except IdentityValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except IdentityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except IdentityConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    return ApiKeyCreatedHttpResponse.from_application(response)

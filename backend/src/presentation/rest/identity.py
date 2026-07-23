from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status

from application.audit.dto import AuditContext
from application.identity.dto import (
    CreateApiKeyRequest,
    CreateServiceAccountRequest,
    CreateSessionRequest,
    CreateUserRequest,
)
from application.identity.exceptions import (
    AuthenticationFailedError,
    IdentityConflictError,
    IdentityNotFoundError,
    IdentityValidationError,
)
from application.identity.use_cases import (
    CreateApiKeyUseCase,
    CreateServiceAccountUseCase,
    CreateSessionUseCase,
    CreateUserUseCase,
    GetCurrentSessionUseCase,
    RevokeCurrentSessionUseCase,
)
from presentation.rest.audit_context import get_audit_context
from presentation.rest.authentication import (
    SESSION_COOKIE_NAME,
    AuthenticatedIdentity,
    get_authenticated_identity,
    get_optional_authenticated_identity,
)
from presentation.rest.dependencies import (
    get_create_api_key_use_case,
    get_create_service_account_use_case,
    get_create_session_use_case,
    get_create_user_use_case,
    get_current_session_use_case,
    get_revoke_current_session_use_case,
)
from presentation.rest.schemas import (
    ApiKeyCreatedHttpResponse,
    CreateApiKeyHttpRequest,
    CreateServiceAccountHttpRequest,
    CreateSessionHttpRequest,
    CreateUserHttpRequest,
    CurrentSessionHttpResponse,
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
GetCurrentSessionUseCaseDependency = Annotated[
    GetCurrentSessionUseCase,
    Depends(get_current_session_use_case),
]
CreateSessionUseCaseDependency = Annotated[
    CreateSessionUseCase,
    Depends(get_create_session_use_case),
]
RevokeCurrentSessionUseCaseDependency = Annotated[
    RevokeCurrentSessionUseCase,
    Depends(get_revoke_current_session_use_case),
]
OptionalIdentityDependency = Annotated[
    AuthenticatedIdentity | None,
    Depends(get_optional_authenticated_identity),
]
AuthenticatedIdentityDependency = Annotated[
    AuthenticatedIdentity,
    Depends(get_authenticated_identity),
]
AuditContextDependency = Annotated[AuditContext, Depends(get_audit_context)]
SESSION_COOKIE_MAX_AGE_SECONDS = 12 * 60 * 60


@router.post(
    "/auth/session",
    status_code=status.HTTP_201_CREATED,
    response_model=CurrentSessionHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid session data."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Invalid authentication credentials."},
    },
)
async def create_session(
    payload: CreateSessionHttpRequest,
    response: Response,
    use_case: CreateSessionUseCaseDependency,
    audit_context: AuditContextDependency,
) -> CurrentSessionHttpResponse:
    try:
        created = await use_case.execute(
            CreateSessionRequest(api_key=payload.api_key, audit_context=audit_context)
        )
    except IdentityValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except AuthenticationFailedError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
        ) from exc

    response.set_cookie(
        SESSION_COOKIE_NAME,
        created.session_token,
        httponly=True,
        max_age=SESSION_COOKIE_MAX_AGE_SECONDS,
        samesite="lax",
        secure=False,
    )
    return CurrentSessionHttpResponse.from_application(created.session)


@router.get(
    "/auth/session",
    response_model=CurrentSessionHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid authenticated session."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_404_NOT_FOUND: {"description": "Authenticated identity not found."},
    },
)
async def get_current_session(
    identity: AuthenticatedIdentityDependency,
    use_case: GetCurrentSessionUseCaseDependency,
) -> CurrentSessionHttpResponse:
    try:
        response = await use_case.execute(identity.api_key_id, session_id=identity.session_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid session."
        ) from exc
    except AuthenticationFailedError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
        ) from exc
    except IdentityValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except IdentityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return CurrentSessionHttpResponse.from_application(response)


@router.delete(
    "/auth/session",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."}},
)
async def revoke_current_session(
    identity: AuthenticatedIdentityDependency,
    use_case: RevokeCurrentSessionUseCaseDependency,
    audit_context: AuditContextDependency,
) -> Response:
    await use_case.execute(identity.session_id, audit_context=audit_context)
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie(SESSION_COOKIE_NAME, samesite="lax", secure=False)
    return response


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

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response, status

from application.audit.dto import AuditContext
from application.identity.dto import (
    ChangePasswordRequest,
    CreateApiKeyRequest,
    CreateServiceAccountRequest,
    CreateSessionRequest,
    CreateUserRequest,
    GetApiKeyRequest,
    GetProfileRequest,
    GetSettingsRequest,
    ListActiveSessionsRequest,
    ListApiKeysRequest,
    RevokeApiKeyRequest,
    RevokeSessionRequest,
    UpdateApiKeyRequest,
    UpdateNotificationsRequest,
    UpdatePreferencesRequest,
    UpdateProfileRequest,
)
from application.identity.exceptions import (
    AuthenticationFailedError,
    IdentityConflictError,
    IdentityNotFoundError,
    IdentityValidationError,
)
from application.identity.use_cases import (
    ChangePasswordUseCase,
    CreateApiKeyUseCase,
    CreateServiceAccountUseCase,
    CreateSessionUseCase,
    CreateUserUseCase,
    GetAccountSecurityUseCase,
    GetApiKeyUseCase,
    GetCurrentProfileUseCase,
    GetCurrentSessionUseCase,
    GetSettingsUseCase,
    ListActiveSessionsUseCase,
    ListApiKeysUseCase,
    RevokeApiKeyUseCase,
    RevokeCurrentSessionUseCase,
    RevokeSessionUseCase,
    UpdateApiKeyUseCase,
    UpdateCurrentProfileUseCase,
    UpdateNotificationsUseCase,
    UpdatePreferencesUseCase,
)
from presentation.rest.audit_context import get_audit_context
from presentation.rest.authentication import (
    CSRF_COOKIE_NAME,
    SESSION_COOKIE_NAME,
    AuthenticatedIdentity,
    generate_csrf_token,
    get_authenticated_identity,
    get_optional_authenticated_identity,
)
from presentation.rest.authorization import permission_required
from presentation.rest.dependencies import (
    get_account_security_use_case,
    get_api_key_use_case,
    get_change_password_use_case,
    get_create_api_key_use_case,
    get_create_service_account_use_case,
    get_create_session_use_case,
    get_create_user_use_case,
    get_current_profile_use_case,
    get_current_session_use_case,
    get_list_active_sessions_use_case,
    get_list_api_keys_use_case,
    get_revoke_api_key_use_case,
    get_revoke_current_session_use_case,
    get_revoke_session_use_case,
    get_settings_use_case,
    get_update_api_key_use_case,
    get_update_current_profile_use_case,
    get_update_notifications_use_case,
    get_update_preferences_use_case,
)
from presentation.rest.schemas import (
    AccountSecurityHttpResponse,
    ActiveSessionListHttpResponse,
    ApiKeyCreatedHttpResponse,
    ApiKeyHttpResponse,
    ApiKeyListHttpResponse,
    ChangePasswordHttpRequest,
    CreateApiKeyHttpRequest,
    CreateServiceAccountHttpRequest,
    CreateSessionHttpRequest,
    CreateUserHttpRequest,
    CurrentSessionHttpResponse,
    NotificationPreferencesHttpResponse,
    ServiceAccountHttpResponse,
    SettingsHttpResponse,
    UpdateApiKeyHttpRequest,
    UpdateNotificationsHttpRequest,
    UpdatePreferencesHttpRequest,
    UpdateProfileHttpRequest,
    UserHttpResponse,
    UserPreferencesHttpResponse,
    UserProfileHttpResponse,
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
ListApiKeysUseCaseDependency = Annotated[
    ListApiKeysUseCase,
    Depends(get_list_api_keys_use_case),
]
GetApiKeyUseCaseDependency = Annotated[
    GetApiKeyUseCase,
    Depends(get_api_key_use_case),
]
RevokeApiKeyUseCaseDependency = Annotated[
    RevokeApiKeyUseCase,
    Depends(get_revoke_api_key_use_case),
]
UpdateApiKeyUseCaseDependency = Annotated[
    UpdateApiKeyUseCase,
    Depends(get_update_api_key_use_case),
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
GetCurrentProfileUseCaseDependency = Annotated[
    GetCurrentProfileUseCase,
    Depends(get_current_profile_use_case),
]
UpdateCurrentProfileUseCaseDependency = Annotated[
    UpdateCurrentProfileUseCase,
    Depends(get_update_current_profile_use_case),
]
GetAccountSecurityUseCaseDependency = Annotated[
    GetAccountSecurityUseCase,
    Depends(get_account_security_use_case),
]
ListActiveSessionsUseCaseDependency = Annotated[
    ListActiveSessionsUseCase,
    Depends(get_list_active_sessions_use_case),
]
RevokeSessionUseCaseDependency = Annotated[
    RevokeSessionUseCase,
    Depends(get_revoke_session_use_case),
]
ChangePasswordUseCaseDependency = Annotated[
    ChangePasswordUseCase,
    Depends(get_change_password_use_case),
]
GetSettingsUseCaseDependency = Annotated[
    GetSettingsUseCase,
    Depends(get_settings_use_case),
]
UpdatePreferencesUseCaseDependency = Annotated[
    UpdatePreferencesUseCase,
    Depends(get_update_preferences_use_case),
]
UpdateNotificationsUseCaseDependency = Annotated[
    UpdateNotificationsUseCase,
    Depends(get_update_notifications_use_case),
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


def use_secure_cookies(request: Request) -> bool:
    return bool(getattr(request.app.state, "secure_cookies", False))


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
    request: Request,
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

    secure_cookies = use_secure_cookies(request)
    response.set_cookie(
        SESSION_COOKIE_NAME,
        created.session_token,
        httponly=True,
        max_age=SESSION_COOKIE_MAX_AGE_SECONDS,
        samesite="lax",
        secure=secure_cookies,
    )
    response.set_cookie(
        CSRF_COOKIE_NAME,
        generate_csrf_token(),
        httponly=False,
        max_age=SESSION_COOKIE_MAX_AGE_SECONDS,
        samesite="lax",
        secure=secure_cookies,
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
    request: Request,
    identity: AuthenticatedIdentityDependency,
    use_case: RevokeCurrentSessionUseCaseDependency,
    audit_context: AuditContextDependency,
) -> Response:
    await use_case.execute(identity.session_id, audit_context=audit_context)
    secure_cookies = use_secure_cookies(request)
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    response.delete_cookie(SESSION_COOKIE_NAME, samesite="lax", secure=secure_cookies)
    response.delete_cookie(CSRF_COOKIE_NAME, samesite="lax", secure=secure_cookies)
    return response


@router.get(
    "/me/profile",
    response_model=UserProfileHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid authenticated identity."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_404_NOT_FOUND: {"description": "Authenticated profile not found."},
    },
)
async def get_current_profile(
    identity: AuthenticatedIdentityDependency,
    use_case: GetCurrentProfileUseCaseDependency,
) -> UserProfileHttpResponse:
    try:
        response = await use_case.execute(
            GetProfileRequest(identity_id=identity.id, identity_type=identity.type)
        )
    except IdentityValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except IdentityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return UserProfileHttpResponse.from_application(response)


@router.patch(
    "/me/profile",
    response_model=UserProfileHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid profile data."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_404_NOT_FOUND: {"description": "Authenticated profile not found."},
    },
)
async def update_current_profile(
    payload: UpdateProfileHttpRequest,
    identity: AuthenticatedIdentityDependency,
    use_case: UpdateCurrentProfileUseCaseDependency,
    audit_context: AuditContextDependency,
) -> UserProfileHttpResponse:
    try:
        response = await use_case.execute(
            UpdateProfileRequest(
                identity_id=identity.id,
                identity_type=identity.type,
                email=payload.email,
                name=payload.name,
                organization=payload.organization,
                audit_context=audit_context,
            )
        )
    except IdentityValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except IdentityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return UserProfileHttpResponse.from_application(response)


@router.get(
    "/me/security",
    response_model=AccountSecurityHttpResponse,
    responses={status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."}},
)
async def get_account_security(
    _identity: AuthenticatedIdentityDependency,
    use_case: GetAccountSecurityUseCaseDependency,
) -> AccountSecurityHttpResponse:
    return AccountSecurityHttpResponse.from_application(await use_case.execute())


@router.get(
    "/me/sessions",
    response_model=ActiveSessionListHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid authenticated identity."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
    },
)
async def list_active_sessions(
    identity: AuthenticatedIdentityDependency,
    use_case: ListActiveSessionsUseCaseDependency,
) -> ActiveSessionListHttpResponse:
    try:
        response = await use_case.execute(
            ListActiveSessionsRequest(
                identity_id=identity.id,
                identity_type=identity.type,
                current_session_id=identity.session_id,
            )
        )
    except IdentityValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ActiveSessionListHttpResponse.from_application(response)


@router.delete(
    "/me/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid session id."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_404_NOT_FOUND: {"description": "Session not found."},
    },
)
async def revoke_session(
    session_id: str,
    identity: AuthenticatedIdentityDependency,
    use_case: RevokeSessionUseCaseDependency,
    audit_context: AuditContextDependency,
) -> Response:
    try:
        await use_case.execute(
            RevokeSessionRequest(
                identity_id=identity.id,
                identity_type=identity.type,
                session_id=session_id,
                current_session_id=identity.session_id,
                audit_context=audit_context,
            )
        )
    except IdentityValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except IdentityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/me/password",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid password data."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
    },
)
async def change_password(
    payload: ChangePasswordHttpRequest,
    identity: AuthenticatedIdentityDependency,
    use_case: ChangePasswordUseCaseDependency,
    audit_context: AuditContextDependency,
) -> Response:
    try:
        await use_case.execute(
            ChangePasswordRequest(
                identity_id=identity.id,
                identity_type=identity.type,
                current_password=payload.current_password,
                new_password=payload.new_password,
                audit_context=audit_context,
            )
        )
    except IdentityValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/me/settings",
    response_model=SettingsHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid authenticated identity."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
    },
)
async def get_settings(
    identity: AuthenticatedIdentityDependency,
    use_case: GetSettingsUseCaseDependency,
) -> SettingsHttpResponse:
    try:
        response = await use_case.execute(
            GetSettingsRequest(identity_id=identity.id, identity_type=identity.type)
        )
    except IdentityValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return SettingsHttpResponse.from_application(response)


@router.patch(
    "/me/preferences",
    response_model=UserPreferencesHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid preference data."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
    },
)
async def update_preferences(
    payload: UpdatePreferencesHttpRequest,
    identity: AuthenticatedIdentityDependency,
    use_case: UpdatePreferencesUseCaseDependency,
    audit_context: AuditContextDependency,
) -> UserPreferencesHttpResponse:
    try:
        response = await use_case.execute(
            UpdatePreferencesRequest(
                identity_id=identity.id,
                identity_type=identity.type,
                date_time_format=payload.date_time_format,
                display_density=payload.display_density,
                language=payload.language,
                theme=payload.theme,
                timezone=payload.timezone,
                audit_context=audit_context,
            )
        )
    except IdentityValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return UserPreferencesHttpResponse.from_application(response)


@router.patch(
    "/me/notifications",
    response_model=NotificationPreferencesHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid notification data."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
    },
)
async def update_notifications(
    payload: UpdateNotificationsHttpRequest,
    identity: AuthenticatedIdentityDependency,
    use_case: UpdateNotificationsUseCaseDependency,
    audit_context: AuditContextDependency,
) -> NotificationPreferencesHttpResponse:
    try:
        response = await use_case.execute(
            UpdateNotificationsRequest(
                identity_id=identity.id,
                identity_type=identity.type,
                audit_alerts=payload.audit_alerts,
                email_enabled=payload.email_enabled,
                in_app_enabled=payload.in_app_enabled,
                product_updates=payload.product_updates,
                security_alerts=payload.security_alerts,
                audit_context=audit_context,
            )
        )
    except IdentityValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return NotificationPreferencesHttpResponse.from_application(response)


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
    "/tokens",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiKeyCreatedHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid API key data."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "API key create permission is required."},
        status.HTTP_404_NOT_FOUND: {"description": "Owner not found."},
        status.HTTP_409_CONFLICT: {"description": "API key conflict."},
    },
    dependencies=[Depends(permission_required("apikey.create", "global"))],
)
@router.post(
    "/api-keys",
    status_code=status.HTTP_201_CREATED,
    response_model=ApiKeyCreatedHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid API key data."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "API key create permission is required."},
        status.HTTP_404_NOT_FOUND: {"description": "Owner not found."},
        status.HTTP_409_CONFLICT: {"description": "API key conflict."},
    },
    dependencies=[Depends(permission_required("apikey.create", "global"))],
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
                name=payload.name,
                description=payload.description,
                granted_permissions=tuple(payload.permissions),
                scopes=tuple(payload.scopes),
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


@router.get(
    "/tokens",
    response_model=ApiKeyListHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid API key list filters."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "API key read permission is required."},
    },
    dependencies=[Depends(permission_required("apikey.read", "global"))],
)
@router.get(
    "/api-keys",
    response_model=ApiKeyListHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid API key list filters."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "API key read permission is required."},
    },
    dependencies=[Depends(permission_required("apikey.read", "global"))],
)
async def list_api_keys(
    use_case: ListApiKeysUseCaseDependency,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(alias="page_size", ge=1, le=100)] = 20,
    search: str | None = None,
    q: str | None = None,
    status_filter: Annotated[str | None, Query(alias="status")] = None,
) -> ApiKeyListHttpResponse:
    try:
        response = await use_case.execute(
            ListApiKeysRequest(
                page=page,
                page_size=page_size,
                search=search or q,
                status=status_filter,
            )
        )
    except IdentityValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return ApiKeyListHttpResponse.from_application(response)


@router.get(
    "/tokens/{api_key_id}",
    response_model=ApiKeyHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid API key id."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "API key read permission is required."},
        status.HTTP_404_NOT_FOUND: {"description": "API key not found."},
    },
    dependencies=[Depends(permission_required("apikey.read", "global"))],
)
@router.get(
    "/api-keys/{api_key_id}",
    response_model=ApiKeyHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid API key id."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "API key read permission is required."},
        status.HTTP_404_NOT_FOUND: {"description": "API key not found."},
    },
    dependencies=[Depends(permission_required("apikey.read", "global"))],
)
async def get_api_key(
    api_key_id: str,
    use_case: GetApiKeyUseCaseDependency,
    audit_context: AuditContextDependency,
) -> ApiKeyHttpResponse:
    try:
        response = await use_case.execute(
            GetApiKeyRequest(api_key_id=api_key_id, audit_context=audit_context)
        )
    except IdentityValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except IdentityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ApiKeyHttpResponse.from_application(response)


@router.patch(
    "/tokens/{api_key_id}",
    response_model=ApiKeyHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid API key data."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "API key update permission is required."},
        status.HTTP_404_NOT_FOUND: {"description": "API key not found."},
    },
    dependencies=[Depends(permission_required("apikey.update", "global"))],
)
@router.patch(
    "/api-keys/{api_key_id}",
    response_model=ApiKeyHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid API key data."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "API key update permission is required."},
        status.HTTP_404_NOT_FOUND: {"description": "API key not found."},
    },
    dependencies=[Depends(permission_required("apikey.update", "global"))],
)
async def update_api_key(
    api_key_id: str,
    payload: UpdateApiKeyHttpRequest,
    use_case: UpdateApiKeyUseCaseDependency,
    audit_context: AuditContextDependency,
) -> ApiKeyHttpResponse:
    try:
        response = await use_case.execute(
            UpdateApiKeyRequest(
                api_key_id=api_key_id,
                name=payload.name,
                description=payload.description,
                expires_at=payload.expires_at,
                granted_permissions=tuple(payload.permissions),
                scopes=tuple(payload.scopes),
                audit_context=audit_context,
            )
        )
    except IdentityValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except IdentityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ApiKeyHttpResponse.from_application(response)


@router.post(
    "/tokens/{api_key_id}/revoke",
    response_model=ApiKeyHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid API key id."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "API key revoke permission is required."},
        status.HTTP_404_NOT_FOUND: {"description": "API key not found."},
    },
    dependencies=[Depends(permission_required("apikey.revoke", "global"))],
)
@router.post(
    "/api-keys/{api_key_id}/revoke",
    response_model=ApiKeyHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid API key id."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "API key revoke permission is required."},
        status.HTTP_404_NOT_FOUND: {"description": "API key not found."},
    },
    dependencies=[Depends(permission_required("apikey.revoke", "global"))],
)
async def revoke_api_key(
    api_key_id: str,
    use_case: RevokeApiKeyUseCaseDependency,
    audit_context: AuditContextDependency,
) -> ApiKeyHttpResponse:
    try:
        response = await use_case.execute(
            RevokeApiKeyRequest(api_key_id=api_key_id, audit_context=audit_context)
        )
    except IdentityValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except IdentityNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    return ApiKeyHttpResponse.from_application(response)

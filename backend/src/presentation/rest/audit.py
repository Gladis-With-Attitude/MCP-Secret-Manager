from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from application.audit.dto import AuditQueryRequest
from application.audit.exceptions import AuditNotFoundError, AuditValidationError
from application.audit.use_cases import GetAuditEventUseCase, ListAuditEventsUseCase
from presentation.rest.authorization import permission_required
from presentation.rest.dependencies import get_audit_event_use_case, get_list_audit_events_use_case
from presentation.rest.schemas import AuditEventHttpResponse

router = APIRouter(prefix="/v1/audit", tags=["audit"])

ListAuditEventsUseCaseDependency = Annotated[
    ListAuditEventsUseCase,
    Depends(get_list_audit_events_use_case),
]
GetAuditEventUseCaseDependency = Annotated[
    GetAuditEventUseCase,
    Depends(get_audit_event_use_case),
]


@router.get(
    "",
    response_model=list[AuditEventHttpResponse],
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid audit query."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "Audit read permission is required."},
    },
    dependencies=[Depends(permission_required("audit.read", "global"))],
)
@router.get(
    "/events",
    response_model=list[AuditEventHttpResponse],
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid audit query."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "Audit read permission is required."},
    },
    dependencies=[Depends(permission_required("audit.read", "global"))],
)
async def list_audit_events(
    use_case: ListAuditEventsUseCaseDependency,
    start_date: Annotated[str | None, Query()] = None,
    end_date: Annotated[str | None, Query()] = None,
    actor_id: Annotated[str | None, Query()] = None,
    q: Annotated[str | None, Query(max_length=160)] = None,
    search: Annotated[str | None, Query(max_length=160)] = None,
    action: Annotated[str | None, Query()] = None,
    resource_type: Annotated[str | None, Query()] = None,
    resource_id: Annotated[str | None, Query()] = None,
    result: Annotated[str | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=500)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[AuditEventHttpResponse]:
    try:
        response = await use_case.execute(
            AuditQueryRequest(
                start_date=start_date,
                end_date=end_date,
                actor_id=actor_id,
                query=q or search,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                result=result,
                limit=limit,
                offset=offset,
            )
        )
    except AuditValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return [AuditEventHttpResponse.from_application(event) for event in response]


@router.get(
    "/{event_id}",
    response_model=AuditEventHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid audit event id."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "Audit read permission is required."},
        status.HTTP_404_NOT_FOUND: {"description": "Audit event not found."},
    },
    dependencies=[Depends(permission_required("audit.read", "global"))],
)
@router.get(
    "/events/{event_id}",
    response_model=AuditEventHttpResponse,
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid audit event id."},
        status.HTTP_401_UNAUTHORIZED: {"description": "Authentication is required."},
        status.HTTP_403_FORBIDDEN: {"description": "Audit read permission is required."},
        status.HTTP_404_NOT_FOUND: {"description": "Audit event not found."},
    },
    dependencies=[Depends(permission_required("audit.read", "global"))],
)
async def get_audit_event(
    event_id: str,
    use_case: GetAuditEventUseCaseDependency,
) -> AuditEventHttpResponse:
    try:
        event = await use_case.execute(event_id)
    except AuditValidationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except AuditNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return AuditEventHttpResponse.from_application(event)

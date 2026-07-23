from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request

from application.audit.dto import AuditContext
from presentation.rest.authentication import (
    AuthenticatedIdentity,
    get_optional_authenticated_identity,
)
from presentation.rest.observability import get_or_create_request_id

OptionalIdentityDependency = Annotated[
    AuthenticatedIdentity | None,
    Depends(get_optional_authenticated_identity),
]


def get_audit_context(
    request: Request,
    identity: OptionalIdentityDependency,
) -> AuditContext:
    request_id = get_or_create_request_id(request)

    client_host = request.client.host if request.client is not None else None
    return AuditContext(
        actor_id=identity.id if identity is not None else None,
        actor_type=identity.type if identity is not None else "anonymous",
        ip_address=client_host,
        user_agent=request.headers.get("User-Agent"),
        request_id=request_id,
    )

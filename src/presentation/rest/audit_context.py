from __future__ import annotations

from typing import Annotated
from uuid import uuid4

from fastapi import Depends, Request

from application.audit.dto import AuditContext
from presentation.rest.authentication import (
    AuthenticatedIdentity,
    get_optional_authenticated_identity,
)

OptionalIdentityDependency = Annotated[
    AuthenticatedIdentity | None,
    Depends(get_optional_authenticated_identity),
]


def get_audit_context(
    request: Request,
    identity: OptionalIdentityDependency,
) -> AuditContext:
    request_id = getattr(request.state, "request_id", None)
    if not isinstance(request_id, str):
        request_id = request.headers.get("X-Request-ID") or str(uuid4())
        request.state.request_id = request_id

    client_host = request.client.host if request.client is not None else None
    return AuditContext(
        actor_id=identity.id if identity is not None else None,
        actor_type=identity.type if identity is not None else "anonymous",
        ip_address=client_host,
        user_agent=request.headers.get("User-Agent"),
        request_id=request_id,
    )

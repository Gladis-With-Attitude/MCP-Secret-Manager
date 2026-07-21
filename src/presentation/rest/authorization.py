from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status

from application.rbac.dto import RequirePermission
from application.rbac.exceptions import AuthorizationDeniedError, RbacValidationError
from application.rbac.use_cases import AuthorizeUseCase
from presentation.rest.authentication import AuthenticatedIdentity, get_authenticated_identity
from presentation.rest.dependencies import get_authorize_use_case

AuthenticatedIdentityDependency = Annotated[
    AuthenticatedIdentity,
    Depends(get_authenticated_identity),
]
AuthorizeUseCaseDependency = Annotated[AuthorizeUseCase, Depends(get_authorize_use_case)]


def permission_required(
    permission: str,
    scope_type: str,
    scope_id: str | None = None,
    parent_vault_id: str | None = None,
    parent_project_id: str | None = None,
) -> Callable[[AuthenticatedIdentityDependency, AuthorizeUseCaseDependency], Awaitable[None]]:
    async def dependency(
        identity: AuthenticatedIdentityDependency,
        use_case: AuthorizeUseCaseDependency,
    ) -> None:
        try:
            await use_case.execute(
                RequirePermission(
                    identity_id=identity.id,
                    identity_type=identity.type,
                    permission=permission,
                    scope_type=scope_type,
                    scope_id=scope_id,
                    parent_vault_id=parent_vault_id,
                    parent_project_id=parent_project_id,
                )
            )
        except RbacValidationError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        except AuthorizationDeniedError as exc:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden.") from exc

    return dependency

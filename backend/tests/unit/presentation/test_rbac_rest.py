from __future__ import annotations

from collections.abc import AsyncIterator

import anyio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from application.rbac.dto import (
    AssignActorRoleRequest,
    AuthorizationDecision,
    CreateRoleRequest,
    GetRoleRequest,
    ListActorRolesRequest,
    ListRolesRequest,
    PermissionListResponse,
    PermissionResponse,
    RequirePermission,
    RevokeActorRoleRequest,
    RoleListResponse,
    RolePermissionsResponse,
    RoleResponse,
    UpdateRoleRequest,
    UserRoleListResponse,
    UserRoleResponse,
)
from presentation.rest.app import create_app
from presentation.rest.authentication import AuthenticatedIdentity, get_authenticated_identity
from presentation.rest.dependencies import (
    get_assign_actor_role_use_case,
    get_authorize_use_case,
    get_create_role_use_case,
    get_list_actor_roles_use_case,
    get_list_permissions_use_case,
    get_list_roles_use_case,
    get_revoke_actor_role_use_case,
    get_role_use_case,
    get_update_role_use_case,
)

ROLE_ID = "4f33c01d-819d-4a6e-b8e4-6caf7a1213ef"
PERMISSION_ID = "027e0bf6-6d6a-4f52-86cc-53621ee0b5d2"
ACTOR_ID = "16b837e2-9a7e-4d20-89bf-8815d4cad7a5"
ASSIGNMENT_ID = "cbf67df2-5f35-4c7e-a36a-7e441fd63a7f"


class RecordingAuthorizeUseCase:
    def __init__(self) -> None:
        self.requests: list[RequirePermission] = []

    async def execute(self, request: RequirePermission) -> AuthorizationDecision:
        self.requests.append(request)
        return AuthorizationDecision(allowed=True)


class FakeListPermissionsUseCase:
    async def execute(self) -> PermissionListResponse:
        return PermissionListResponse(data=(_permission_response(),))


class FakeListRolesUseCase:
    async def execute(self, request: ListRolesRequest) -> RoleListResponse:
        return RoleListResponse(
            data=(_role_response(name=request.search or "reader"),),
            limit=request.limit,
            offset=request.offset,
            total=1,
            permissions=_role_permissions(),
        )


class FakeGetRoleUseCase:
    async def execute(self, request: GetRoleRequest) -> RoleResponse:
        return _role_response(role_id=request.role_id)


class FakeCreateRoleUseCase:
    async def execute(self, request: CreateRoleRequest) -> RoleResponse:
        return _role_response(name=request.name, description=request.description)


class FakeUpdateRoleUseCase:
    async def execute(self, request: UpdateRoleRequest) -> RoleResponse:
        return _role_response(role_id=request.role_id, name=request.name)


class FakeListActorRolesUseCase:
    async def execute(self, request: ListActorRolesRequest) -> UserRoleListResponse:
        return UserRoleListResponse(
            actor_id=request.actor_id,
            data=(_user_role_response(actor_id=request.actor_id),),
            permissions=_role_permissions(),
        )


class FakeAssignActorRoleUseCase:
    async def execute(self, request: AssignActorRoleRequest) -> UserRoleResponse:
        return _user_role_response(actor_id=request.actor_id, role_id=request.role_id)


class FakeRevokeActorRoleUseCase:
    async def execute(self, request: RevokeActorRoleRequest) -> UserRoleResponse:
        return _user_role_response(
            actor_id=request.actor_id,
            role_id=request.role_id,
            status="revoked",
        )


def _permission_response() -> PermissionResponse:
    return PermissionResponse(
        id=PERMISSION_ID,
        name="role.read",
        description="Read roles.",
        resource="role",
        action="read",
        group="role",
        sensitivity="standard",
    )


def _role_permissions() -> RolePermissionsResponse:
    return RolePermissionsResponse(assign=True, create=True, read=True, revoke=True, update=True)


def _role_response(
    *,
    role_id: str = ROLE_ID,
    name: str = "reader",
    description: str | None = "Read metadata.",
) -> RoleResponse:
    return RoleResponse(
        id=role_id,
        name=name,
        description=description,
        kind="custom",
        is_system=False,
        permission_ids=(PERMISSION_ID,),
        permissions=(_permission_response(),),
        permissions_count=1,
        assignments_count=1,
        status="active",
        ui_permissions=_role_permissions(),
    )


def _user_role_response(
    *,
    actor_id: str = ACTOR_ID,
    role_id: str = ROLE_ID,
    status: str = "active",
) -> UserRoleResponse:
    return UserRoleResponse(
        id=ASSIGNMENT_ID,
        actor_id=actor_id,
        role_id=role_id,
        role_name="reader",
        scope_type="global",
        scope_id=None,
        status=status,
        assigned_at="2026-07-23T12:00:00+00:00",
    )


def build_rbac_app(authorize_use_case: RecordingAuthorizeUseCase) -> FastAPI:
    app = create_app(service_name="test-service")
    app.dependency_overrides[get_authenticated_identity] = lambda: AuthenticatedIdentity(
        id=ACTOR_ID,
        type="user",
        api_key_id="445bec4f-5379-4d61-8876-47886c49ea05",
    )

    async def authorize_dependency() -> AsyncIterator[RecordingAuthorizeUseCase]:
        yield authorize_use_case

    app.dependency_overrides[get_authorize_use_case] = authorize_dependency
    app.dependency_overrides[get_list_permissions_use_case] = lambda: FakeListPermissionsUseCase()
    app.dependency_overrides[get_list_roles_use_case] = lambda: FakeListRolesUseCase()
    app.dependency_overrides[get_role_use_case] = lambda: FakeGetRoleUseCase()
    app.dependency_overrides[get_create_role_use_case] = lambda: FakeCreateRoleUseCase()
    app.dependency_overrides[get_update_role_use_case] = lambda: FakeUpdateRoleUseCase()
    app.dependency_overrides[get_list_actor_roles_use_case] = lambda: FakeListActorRolesUseCase()
    app.dependency_overrides[get_assign_actor_role_use_case] = lambda: FakeAssignActorRoleUseCase()
    app.dependency_overrides[get_revoke_actor_role_use_case] = lambda: FakeRevokeActorRoleUseCase()
    return app


def test_rbac_routes_enforce_expected_permissions() -> None:
    async def run() -> None:
        authorize_use_case = RecordingAuthorizeUseCase()
        app = build_rbac_app(authorize_use_case)
        transport = ASGITransport(app=app)

        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            responses = [
                await client.get("/v1/permissions"),
                await client.get("/v1/roles", params={"q": "reader"}),
                await client.post(
                    "/v1/roles",
                    json={"name": "reader", "permission_ids": [PERMISSION_ID]},
                ),
                await client.get(f"/v1/roles/{ROLE_ID}"),
                await client.patch(
                    f"/v1/roles/{ROLE_ID}",
                    json={"name": "reader", "permission_ids": [PERMISSION_ID]},
                ),
                await client.get(f"/v1/actors/{ACTOR_ID}/roles"),
                await client.post(f"/v1/actors/{ACTOR_ID}/roles/{ROLE_ID}"),
                await client.delete(f"/v1/actors/{ACTOR_ID}/roles/{ROLE_ID}"),
            ]

        assert [response.status_code for response in responses] == [
            200,
            200,
            201,
            200,
            200,
            200,
            201,
            200,
        ]
        assert [request.permission for request in authorize_use_case.requests] == [
            "role.read",
            "role.read",
            "role.create",
            "role.read",
            "role.update",
            "role.read",
            "role.assign",
            "role.revoke",
        ]
        assert {request.scope_type for request in authorize_use_case.requests} == {"global"}

    anyio.run(run)

from __future__ import annotations

from collections.abc import AsyncIterator, Mapping
from typing import cast

import anyio
import pytest
from httpx import ASGITransport, AsyncClient

from application.audit.dto import AuditContext
from application.identity.dto import AuthenticatedIdentityResponse
from application.identity.exceptions import AuthenticationFailedError
from application.identity.use_cases import AuthenticateApiKeyUseCase
from application.project.dto import (
    CreateProjectRequest,
    ProjectListResponse,
    ProjectPermissionsResponse,
    ProjectResponse,
)
from application.project.dto import (
    PaginationResponse as ProjectPaginationResponse,
)
from application.project.use_cases import CreateProjectUseCase, ListProjectsUseCase
from application.rbac.dto import AuthorizationDecision, RequirePermission
from application.rbac.exceptions import AuthorizationDeniedError
from application.rbac.use_cases import AuthorizeUseCase
from application.secret.dto import (
    CreateSecretRequest,
    GetSecretRequest,
    ListSecretsRequest,
    SearchSecretsRequest,
    SecretResponse,
)
from application.secret.use_cases import (
    CreateSecretUseCase,
    GetSecretUseCase,
    ListSecretsUseCase,
    SearchSecretsUseCase,
)
from application.secret_version.dto import (
    CreateSecretVersionRequest,
    SecretVersionMetadataResponse,
    SecretVersionResponse,
)
from application.secret_version.use_cases import (
    CreateSecretVersionUseCase,
    GetActiveSecretVersionUseCase,
    ListSecretVersionsUseCase,
)
from application.vault.dto import (
    CreateVaultRequest,
    PaginationResponse,
    VaultListResponse,
    VaultPermissionsResponse,
    VaultResponse,
)
from application.vault.use_cases import CreateVaultUseCase, ListVaultsUseCase
from presentation.mcp.server import McpServer
from presentation.mcp.tools import SecretManagerMcpTools
from presentation.mcp.types import (
    McpAuthContext,
    McpAuthenticationError,
    McpAuthorizationError,
)
from presentation.rest.app import create_app
from presentation.rest.authentication import AuthenticatedIdentity, get_authenticated_identity
from presentation.rest.dependencies import get_authorize_use_case, get_create_vault_use_case


class FakeAuthenticateApiKeyUseCase:
    async def execute(
        self,
        raw_api_key: str,
        audit_context: AuditContext | None = None,
    ) -> AuthenticatedIdentityResponse:
        assert audit_context is not None
        assert audit_context.protocol == "mcp"
        if raw_api_key != "valid-api-key":
            raise AuthenticationFailedError("Invalid API key.")
        return AuthenticatedIdentityResponse(
            id="a6ef559c-b860-4028-a050-bb7bd2244916",
            type="user",
            api_key_id="71a35966-aa7e-48af-815a-77796de636af",
        )


class FakeAuthorizeUseCase:
    def __init__(self, allowed: bool = True) -> None:
        self.allowed = allowed
        self.requests: list[RequirePermission] = []

    async def execute(self, request: RequirePermission) -> AuthorizationDecision:
        self.requests.append(request)
        if not self.allowed:
            raise AuthorizationDeniedError("Permission denied.")
        return AuthorizationDecision(allowed=True)


class FakeListVaultsUseCase:
    async def execute(self) -> VaultListResponse:
        return VaultListResponse(
            data=(VaultResponse(id="vault-1", name="Production"),),
            pagination=PaginationResponse(
                page=1,
                page_size=20,
                total=1,
                has_next_page=False,
                has_previous_page=False,
            ),
            permissions=VaultPermissionsResponse(
                create=True,
                read=True,
                update=True,
                archive=True,
                lock=False,
            ),
        )


class FakeCreateVaultUseCase:
    def __init__(self) -> None:
        self.requests: list[CreateVaultRequest] = []

    async def execute(self, request: CreateVaultRequest) -> VaultResponse:
        self.requests.append(request)
        return VaultResponse(id="vault-1", name=request.name.strip())


class FakeListProjectsUseCase:
    async def execute(self, vault_id: str) -> ProjectListResponse:
        return ProjectListResponse(
            data=(ProjectResponse(id="project-1", vault_id=vault_id, name="API"),),
            pagination=ProjectPaginationResponse(
                page=1,
                page_size=20,
                total=1,
                has_next_page=False,
                has_previous_page=False,
            ),
            permissions=ProjectPermissionsResponse(
                create=True,
                read=True,
                update=True,
                archive=True,
                delete=False,
            ),
        )


class FakeCreateProjectUseCase:
    async def execute(self, request: CreateProjectRequest) -> ProjectResponse:
        return ProjectResponse(id="project-1", vault_id=request.vault_id, name=request.name)


class FakeListSecretsUseCase:
    async def execute(self, request: ListSecretsRequest) -> tuple[SecretResponse, ...]:
        return (
            SecretResponse(
                id="secret-1", project_id=request.project_id, key="API_KEY", description=None
            ),
        )


class FakeCreateSecretUseCase:
    async def execute(self, request: CreateSecretRequest) -> SecretResponse:
        return SecretResponse(
            id="secret-1",
            project_id=request.project_id,
            key=request.key,
            description=request.description,
        )


class FakeGetSecretUseCase:
    async def execute(self, request: GetSecretRequest) -> SecretResponse:
        return SecretResponse(
            id=request.secret_id, project_id=request.project_id, key="API_KEY", description=None
        )


class FakeCreateSecretVersionUseCase:
    def __init__(self) -> None:
        self.requests: list[CreateSecretVersionRequest] = []

    async def execute(self, request: CreateSecretVersionRequest) -> SecretVersionResponse:
        self.requests.append(request)
        return SecretVersionResponse(
            id="version-1",
            secret_id=request.secret_id,
            value=request.value,
            version=1,
            active=True,
            created_at="2026-07-21T12:00:00+00:00",
        )


class FakeListSecretVersionsUseCase:
    async def execute(
        self,
        secret_id: str,
        audit_context: AuditContext | None = None,
        project_id: str | None = None,
    ) -> tuple[SecretVersionMetadataResponse, ...]:
        assert audit_context is not None
        assert audit_context.protocol == "mcp"
        assert project_id == "project-1"
        return (
            SecretVersionMetadataResponse(
                id="version-1",
                secret_id=secret_id,
                version=1,
                active=True,
                created_at="2026-07-21T12:00:00+00:00",
            ),
        )


class FakeGetActiveSecretVersionUseCase:
    async def execute(
        self,
        secret_id: str,
        audit_context: AuditContext | None = None,
        project_id: str | None = None,
    ) -> SecretVersionResponse:
        assert audit_context is not None
        assert project_id == "project-1"
        return SecretVersionResponse(
            id="version-1",
            secret_id=secret_id,
            value="secret-value",
            version=1,
            active=True,
            created_at="2026-07-21T12:00:00+00:00",
        )


class FakeSearchSecretsUseCase:
    async def execute(self, request: SearchSecretsRequest) -> tuple[SecretResponse, ...]:
        return (
            SecretResponse(
                id="secret-1", project_id=request.project_id, key="API_KEY", description=None
            ),
        )


def build_server(
    authorize_use_case: FakeAuthorizeUseCase | None = None,
    create_vault_use_case: FakeCreateVaultUseCase | None = None,
    create_secret_version_use_case: FakeCreateSecretVersionUseCase | None = None,
) -> tuple[McpServer, FakeAuthorizeUseCase, FakeCreateVaultUseCase, FakeCreateSecretVersionUseCase]:
    resolved_authorize_use_case = authorize_use_case or FakeAuthorizeUseCase()
    resolved_create_vault_use_case = create_vault_use_case or FakeCreateVaultUseCase()
    resolved_create_secret_version_use_case = (
        create_secret_version_use_case or FakeCreateSecretVersionUseCase()
    )
    server = McpServer(name="test-service")
    tools = SecretManagerMcpTools(
        service_name="test-service",
        authenticate_api_key_use_case=cast(
            AuthenticateApiKeyUseCase,
            FakeAuthenticateApiKeyUseCase(),
        ),
        authorize_use_case=cast(AuthorizeUseCase, resolved_authorize_use_case),
        list_vaults_use_case=cast(ListVaultsUseCase, FakeListVaultsUseCase()),
        create_vault_use_case=cast(CreateVaultUseCase, resolved_create_vault_use_case),
        list_projects_use_case=cast(ListProjectsUseCase, FakeListProjectsUseCase()),
        create_project_use_case=cast(CreateProjectUseCase, FakeCreateProjectUseCase()),
        list_secrets_use_case=cast(ListSecretsUseCase, FakeListSecretsUseCase()),
        create_secret_use_case=cast(CreateSecretUseCase, FakeCreateSecretUseCase()),
        get_secret_use_case=cast(GetSecretUseCase, FakeGetSecretUseCase()),
        create_secret_version_use_case=cast(
            CreateSecretVersionUseCase,
            resolved_create_secret_version_use_case,
        ),
        list_secret_versions_use_case=cast(
            ListSecretVersionsUseCase,
            FakeListSecretVersionsUseCase(),
        ),
        get_active_secret_version_use_case=cast(
            GetActiveSecretVersionUseCase,
            FakeGetActiveSecretVersionUseCase(),
        ),
        search_secrets_use_case=cast(SearchSecretsUseCase, FakeSearchSecretsUseCase()),
    )
    tools.register(server)
    return (
        server,
        resolved_authorize_use_case,
        resolved_create_vault_use_case,
        resolved_create_secret_version_use_case,
    )


def auth_context(api_key: str = "valid-api-key") -> McpAuthContext:
    return McpAuthContext(
        api_key=api_key,
        ip_address="127.0.0.1",
        user_agent="test-agent",
        request_id="req-1",
    )


def test_mcp_server_exposes_required_tools() -> None:
    server, _authorize_use_case, _create_vault_use_case, _version_use_case = build_server()

    names = {tool.name for tool in server.list_tools()}

    assert {
        "list_vaults",
        "create_vault",
        "list_projects",
        "create_project",
        "list_secrets",
        "create_secret",
        "get_secret",
        "create_secret_version",
        "list_secret_versions",
        "rotate_secret",
        "search_secrets",
        "health",
    } <= names


def test_mcp_create_vault_uses_auth_rbac_and_audit_context() -> None:
    async def run() -> None:
        server, authorize_use_case, create_vault_use_case, _version_use_case = build_server()

        result = await server.call_tool(
            "create_vault",
            {"name": "Production"},
            auth_context(),
        )

        assert result.content == {"id": "vault-1", "name": "Production"}
        assert authorize_use_case.requests[0].permission == "vault.create"
        assert authorize_use_case.requests[0].scope_type == "global"
        assert create_vault_use_case.requests[0].audit_context is not None
        assert create_vault_use_case.requests[0].audit_context.protocol == "mcp"

    anyio.run(run)


def test_mcp_rejects_invalid_api_key() -> None:
    async def run() -> None:
        server, _authorize_use_case, _create_vault_use_case, _version_use_case = build_server()

        with pytest.raises(McpAuthenticationError):
            await server.call_tool("list_vaults", {}, auth_context("invalid-api-key"))

    anyio.run(run)


def test_mcp_rejects_rbac_denial() -> None:
    async def run() -> None:
        server, _authorize_use_case, _create_vault_use_case, _version_use_case = build_server(
            authorize_use_case=FakeAuthorizeUseCase(allowed=False)
        )

        with pytest.raises(McpAuthorizationError):
            await server.call_tool("list_vaults", {}, auth_context())

    anyio.run(run)


def test_mcp_rotate_secret_passes_project_scope_to_use_case() -> None:
    async def run() -> None:
        server, authorize_use_case, _create_vault_use_case, version_use_case = build_server()

        result = await server.call_tool(
            "rotate_secret",
            {"project_id": "project-1", "secret_id": "secret-1", "value": "new-value"},
            auth_context(),
        )

        assert isinstance(result.content, Mapping)
        assert result.content["version"] == 1
        assert authorize_use_case.requests[0].permission == "secret.rotate"
        assert authorize_use_case.requests[0].scope_id == "project-1"
        assert version_use_case.requests[0].project_id == "project-1"
        assert version_use_case.requests[0].audit_context is not None
        assert version_use_case.requests[0].audit_context.protocol == "mcp"

    anyio.run(run)


def test_mcp_list_secret_versions_returns_metadata_without_values() -> None:
    async def run() -> None:
        server, authorize_use_case, _create_vault_use_case, _version_use_case = build_server()

        result = await server.call_tool(
            "list_secret_versions",
            {"project_id": "project-1", "secret_id": "secret-1"},
            auth_context(),
        )

        assert result.content == [
            {
                "id": "version-1",
                "secret_id": "secret-1",
                "version": 1,
                "active": True,
                "created_at": "2026-07-21T12:00:00+00:00",
            }
        ]
        assert isinstance(result.content, list)
        first_version = result.content[0]
        assert isinstance(first_version, Mapping)
        assert "value" not in first_version
        assert authorize_use_case.requests[0].permission == "secret.read"

    anyio.run(run)


def test_mcp_json_rpc_tool_call_returns_json_content() -> None:
    async def run() -> None:
        server, _authorize_use_case, _create_vault_use_case, _version_use_case = build_server()

        response = await server.handle_json_rpc(
            {
                "jsonrpc": "2.0",
                "id": "call-1",
                "method": "tools/call",
                "params": {"name": "list_vaults", "arguments": {}},
            },
            auth_context(),
        )

        assert response["result"] == {
            "content": [{"type": "json", "json": [{"id": "vault-1", "name": "Production"}]}]
        }

    anyio.run(run)


def test_rest_and_mcp_create_vault_use_same_application_result() -> None:
    async def run() -> None:
        create_vault_use_case = FakeCreateVaultUseCase()
        server, _authorize_use_case, _mcp_create_vault_use_case, _version_use_case = build_server(
            create_vault_use_case=create_vault_use_case
        )
        app = create_app(service_name="test-service")

        async def create_vault_dependency() -> AsyncIterator[FakeCreateVaultUseCase]:
            yield create_vault_use_case

        async def authorize_dependency() -> AsyncIterator[FakeAuthorizeUseCase]:
            yield FakeAuthorizeUseCase()

        app.dependency_overrides[get_create_vault_use_case] = create_vault_dependency
        app.dependency_overrides[get_authorize_use_case] = authorize_dependency
        app.dependency_overrides[get_authenticated_identity] = lambda: AuthenticatedIdentity(
            id="9d14f3b1-38cc-4447-b69e-e7286fc59d1f",
            type="user",
            api_key_id="aaaaaaaa-aaaa-4aaa-aaaa-aaaaaaaaaaaa",
        )

        mcp_result = await server.call_tool(
            "create_vault",
            {"name": "Production"},
            auth_context(),
        )
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            rest_response = await client.post("/v1/vaults", json={"name": "Production"})

        assert rest_response.status_code == 201
        assert {
            "id": rest_response.json()["id"],
            "name": rest_response.json()["name"],
        } == mcp_result.content

    anyio.run(run)

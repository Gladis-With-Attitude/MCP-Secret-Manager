from __future__ import annotations

from collections.abc import Awaitable, Mapping
from typing import TypeVar

from application.audit.dto import AuditContext
from application.health import get_liveness_status
from application.identity.dto import AuthenticatedIdentityResponse
from application.identity.exceptions import AuthenticationFailedError
from application.identity.use_cases import AuthenticateApiKeyUseCase
from application.project.dto import CreateProjectRequest, ProjectResponse
from application.project.use_cases import CreateProjectUseCase, ListProjectsUseCase
from application.rbac.dto import RequirePermission
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
from application.secret_version.dto import CreateSecretVersionRequest, SecretVersionResponse
from application.secret_version.use_cases import (
    CreateSecretVersionUseCase,
    GetActiveSecretVersionUseCase,
    ListSecretVersionsUseCase,
)
from application.vault.dto import CreateVaultRequest, VaultResponse
from application.vault.use_cases import CreateVaultUseCase, ListVaultsUseCase
from presentation.mcp.server import McpServer
from presentation.mcp.types import (
    JsonObject,
    JsonValue,
    McpAuthContext,
    McpAuthenticationError,
    McpAuthorizationError,
    McpError,
    McpToolDefinition,
    McpToolResult,
    McpValidationError,
)

T = TypeVar("T")


class SecretManagerMcpTools:
    def __init__(
        self,
        service_name: str,
        authenticate_api_key_use_case: AuthenticateApiKeyUseCase,
        authorize_use_case: AuthorizeUseCase,
        list_vaults_use_case: ListVaultsUseCase,
        create_vault_use_case: CreateVaultUseCase,
        list_projects_use_case: ListProjectsUseCase,
        create_project_use_case: CreateProjectUseCase,
        list_secrets_use_case: ListSecretsUseCase,
        create_secret_use_case: CreateSecretUseCase,
        get_secret_use_case: GetSecretUseCase,
        create_secret_version_use_case: CreateSecretVersionUseCase,
        list_secret_versions_use_case: ListSecretVersionsUseCase,
        get_active_secret_version_use_case: GetActiveSecretVersionUseCase,
        search_secrets_use_case: SearchSecretsUseCase,
    ) -> None:
        self._service_name = service_name
        self._authenticate_api_key_use_case = authenticate_api_key_use_case
        self._authorize_use_case = authorize_use_case
        self._list_vaults_use_case = list_vaults_use_case
        self._create_vault_use_case = create_vault_use_case
        self._list_projects_use_case = list_projects_use_case
        self._create_project_use_case = create_project_use_case
        self._list_secrets_use_case = list_secrets_use_case
        self._create_secret_use_case = create_secret_use_case
        self._get_secret_use_case = get_secret_use_case
        self._create_secret_version_use_case = create_secret_version_use_case
        self._list_secret_versions_use_case = list_secret_versions_use_case
        self._get_active_secret_version_use_case = get_active_secret_version_use_case
        self._search_secrets_use_case = search_secrets_use_case

    def register(self, server: McpServer) -> None:
        for definition, handler in (
            (self._tool("health", "Return service health.", {}), self.health),
            (self._tool("list_vaults", "List vaults.", {}), self.list_vaults),
            (self._tool("create_vault", "Create a vault.", {"name": "string"}), self.create_vault),
            (
                self._tool("list_projects", "List projects in a vault.", {"vault_id": "string"}),
                self.list_projects,
            ),
            (
                self._tool(
                    "create_project",
                    "Create a project in a vault.",
                    {"vault_id": "string", "name": "string"},
                ),
                self.create_project,
            ),
            (
                self._tool(
                    "list_secrets",
                    "List secret metadata in a project.",
                    {"project_id": "string"},
                ),
                self.list_secrets,
            ),
            (
                self._tool(
                    "create_secret",
                    "Create secret metadata in a project.",
                    {"project_id": "string", "key": "string", "description": "string|null"},
                ),
                self.create_secret,
            ),
            (
                self._tool(
                    "get_secret",
                    "Get secret metadata.",
                    {"project_id": "string", "secret_id": "string"},
                ),
                self.get_secret,
            ),
            (
                self._tool(
                    "create_secret_version",
                    "Create a new encrypted secret version.",
                    {"project_id": "string", "secret_id": "string", "value": "string"},
                ),
                self.create_secret_version,
            ),
            (
                self._tool(
                    "list_secret_versions",
                    "List decrypted secret versions.",
                    {"project_id": "string", "secret_id": "string"},
                ),
                self.list_secret_versions,
            ),
            (
                self._tool(
                    "rotate_secret",
                    "Rotate a secret value by creating a new version.",
                    {"project_id": "string", "secret_id": "string", "value": "string"},
                ),
                self.rotate_secret,
            ),
            (
                self._tool(
                    "search_secrets",
                    "Search secret metadata by key within a project.",
                    {"project_id": "string", "query": "string"},
                ),
                self.search_secrets,
            ),
        ):
            server.register_tool(definition, handler)

    async def health(
        self,
        arguments: Mapping[str, JsonValue],
        auth_context: McpAuthContext,
    ) -> McpToolResult:
        _ = arguments
        await self._authenticate(auth_context)
        return McpToolResult(get_liveness_status(self._service_name).as_public_dict())

    async def list_vaults(
        self,
        arguments: Mapping[str, JsonValue],
        auth_context: McpAuthContext,
    ) -> McpToolResult:
        _ = arguments
        identity, _audit_context = await self._authenticate(auth_context)
        await self._authorize(identity, "vault.read", "global", None, auth_context)
        response = await self._list_vaults_use_case.execute()
        return McpToolResult([self._vault(item) for item in response.data])

    async def create_vault(
        self,
        arguments: Mapping[str, JsonValue],
        auth_context: McpAuthContext,
    ) -> McpToolResult:
        identity, audit_context = await self._authenticate(auth_context)
        await self._authorize(identity, "vault.create", "global", None, auth_context)
        response = await self._call_application(
            self._create_vault_use_case.execute(
                CreateVaultRequest(
                    name=self._required_string(arguments, "name"),
                    audit_context=audit_context,
                )
            )
        )
        return McpToolResult(self._vault(response))

    async def list_projects(
        self,
        arguments: Mapping[str, JsonValue],
        auth_context: McpAuthContext,
    ) -> McpToolResult:
        vault_id = self._required_string(arguments, "vault_id")
        identity, _audit_context = await self._authenticate(auth_context)
        await self._authorize(identity, "project.read", "vault", vault_id, auth_context)
        response = await self._call_application(self._list_projects_use_case.execute(vault_id))
        return McpToolResult([self._project(item) for item in response.data])

    async def create_project(
        self,
        arguments: Mapping[str, JsonValue],
        auth_context: McpAuthContext,
    ) -> McpToolResult:
        vault_id = self._required_string(arguments, "vault_id")
        identity, audit_context = await self._authenticate(auth_context)
        await self._authorize(identity, "project.create", "vault", vault_id, auth_context)
        response = await self._call_application(
            self._create_project_use_case.execute(
                CreateProjectRequest(
                    vault_id=vault_id,
                    name=self._required_string(arguments, "name"),
                    description=self._optional_string(arguments, "description"),
                    audit_context=audit_context,
                )
            )
        )
        return McpToolResult(self._project(response))

    async def list_secrets(
        self,
        arguments: Mapping[str, JsonValue],
        auth_context: McpAuthContext,
    ) -> McpToolResult:
        project_id = self._required_string(arguments, "project_id")
        identity, audit_context = await self._authenticate(auth_context)
        await self._authorize(identity, "secret.read", "project", project_id, auth_context)
        response = await self._call_application(
            self._list_secrets_use_case.execute(
                ListSecretsRequest(project_id=project_id, audit_context=audit_context)
            )
        )
        return McpToolResult([self._secret(item) for item in response.data])

    async def create_secret(
        self,
        arguments: Mapping[str, JsonValue],
        auth_context: McpAuthContext,
    ) -> McpToolResult:
        project_id = self._required_string(arguments, "project_id")
        identity, audit_context = await self._authenticate(auth_context)
        await self._authorize(identity, "secret.create", "project", project_id, auth_context)
        response = await self._call_application(
            self._create_secret_use_case.execute(
                CreateSecretRequest(
                    project_id=project_id,
                    key=self._required_string(arguments, "key"),
                    description=self._optional_string(arguments, "description"),
                    audit_context=audit_context,
                )
            )
        )
        return McpToolResult(self._secret(response))

    async def get_secret(
        self,
        arguments: Mapping[str, JsonValue],
        auth_context: McpAuthContext,
    ) -> McpToolResult:
        project_id = self._required_string(arguments, "project_id")
        identity, audit_context = await self._authenticate(auth_context)
        await self._authorize(identity, "secret.read", "project", project_id, auth_context)
        response = await self._call_application(
            self._get_secret_use_case.execute(
                GetSecretRequest(
                    project_id=project_id,
                    secret_id=self._required_string(arguments, "secret_id"),
                    audit_context=audit_context,
                )
            )
        )
        return McpToolResult(self._secret(response))

    async def create_secret_version(
        self,
        arguments: Mapping[str, JsonValue],
        auth_context: McpAuthContext,
    ) -> McpToolResult:
        return await self._create_or_rotate_secret(arguments, auth_context)

    async def rotate_secret(
        self,
        arguments: Mapping[str, JsonValue],
        auth_context: McpAuthContext,
    ) -> McpToolResult:
        return await self._create_or_rotate_secret(arguments, auth_context)

    async def list_secret_versions(
        self,
        arguments: Mapping[str, JsonValue],
        auth_context: McpAuthContext,
    ) -> McpToolResult:
        project_id = self._required_string(arguments, "project_id")
        identity, audit_context = await self._authenticate(auth_context)
        await self._authorize(identity, "secret.decrypt", "project", project_id, auth_context)
        response = await self._call_application(
            self._list_secret_versions_use_case.execute(
                self._required_string(arguments, "secret_id"),
                audit_context=audit_context,
                project_id=project_id,
            )
        )
        return McpToolResult([self._secret_version(item) for item in response])

    async def search_secrets(
        self,
        arguments: Mapping[str, JsonValue],
        auth_context: McpAuthContext,
    ) -> McpToolResult:
        project_id = self._required_string(arguments, "project_id")
        identity, audit_context = await self._authenticate(auth_context)
        await self._authorize(identity, "secret.read", "project", project_id, auth_context)
        response = await self._call_application(
            self._search_secrets_use_case.execute(
                SearchSecretsRequest(
                    project_id=project_id,
                    query=self._required_string(arguments, "query"),
                    audit_context=audit_context,
                )
            )
        )
        return McpToolResult([self._secret(item) for item in response])

    async def _create_or_rotate_secret(
        self,
        arguments: Mapping[str, JsonValue],
        auth_context: McpAuthContext,
    ) -> McpToolResult:
        project_id = self._required_string(arguments, "project_id")
        identity, audit_context = await self._authenticate(auth_context)
        await self._authorize(identity, "secret.rotate", "project", project_id, auth_context)
        response = await self._call_application(
            self._create_secret_version_use_case.execute(
                CreateSecretVersionRequest(
                    project_id=project_id,
                    secret_id=self._required_string(arguments, "secret_id"),
                    value=self._required_string(arguments, "value"),
                    audit_context=audit_context,
                )
            )
        )
        return McpToolResult(self._secret_version(response))

    async def _authenticate(
        self,
        auth_context: McpAuthContext,
    ) -> tuple[AuthenticatedIdentityResponse, AuditContext]:
        audit_context = AuditContext(
            actor_type="anonymous",
            ip_address=auth_context.ip_address,
            user_agent=auth_context.user_agent,
            request_id=auth_context.request_id,
            protocol="mcp",
            transport=auth_context.transport,
        )
        try:
            identity = await self._authenticate_api_key_use_case.execute(
                auth_context.api_key,
                audit_context=audit_context,
            )
        except AuthenticationFailedError as exc:
            raise McpAuthenticationError() from exc
        return (
            identity,
            AuditContext(
                actor_id=identity.id,
                actor_type=identity.type,
                ip_address=auth_context.ip_address,
                user_agent=auth_context.user_agent,
                request_id=auth_context.request_id,
                protocol="mcp",
                transport=auth_context.transport,
            ),
        )

    async def _authorize(
        self,
        identity: AuthenticatedIdentityResponse,
        permission: str,
        scope_type: str,
        scope_id: str | None,
        auth_context: McpAuthContext,
    ) -> None:
        try:
            await self._authorize_use_case.execute(
                RequirePermission(
                    identity_id=identity.id,
                    identity_type=identity.type,
                    permission=permission,
                    scope_type=scope_type,
                    scope_id=scope_id,
                    ip_address=auth_context.ip_address,
                    user_agent=auth_context.user_agent,
                    request_id=auth_context.request_id,
                )
            )
        except AuthorizationDeniedError as exc:
            raise McpAuthorizationError() from exc

    @staticmethod
    async def _call_application(awaitable: Awaitable[T]) -> T:
        try:
            return await awaitable
        except McpError:
            raise
        except Exception as exc:
            raise McpError(str(exc), error_code=-32000, app_code="application_error") from exc

    @staticmethod
    def _required_string(arguments: Mapping[str, JsonValue], field_name: str) -> str:
        value = arguments.get(field_name)
        if isinstance(value, str) and value.strip() != "":
            return value
        raise McpValidationError(f"'{field_name}' must be a non-empty string.")

    @staticmethod
    def _optional_string(arguments: Mapping[str, JsonValue], field_name: str) -> str | None:
        value = arguments.get(field_name)
        if value is None:
            return None
        if isinstance(value, str):
            return value
        raise McpValidationError(f"'{field_name}' must be a string or null.")

    @staticmethod
    def _tool(name: str, description: str, properties: Mapping[str, str]) -> McpToolDefinition:
        schema_properties: dict[str, JsonValue] = {
            key: {"type": ["string", "null"] if value.endswith("|null") else value}
            for key, value in properties.items()
        }
        required = [key for key, value in properties.items() if not value.endswith("|null")]
        return McpToolDefinition(
            name=name,
            description=description,
            input_schema={
                "type": "object",
                "properties": schema_properties,
                "required": required,
                "additionalProperties": False,
            },
        )

    @staticmethod
    def _vault(response: VaultResponse) -> JsonObject:
        return {"id": response.id, "name": response.name}

    @staticmethod
    def _project(response: ProjectResponse) -> JsonObject:
        return {
            "id": response.id,
            "vault_id": response.vault_id,
            "name": response.name,
        }

    @staticmethod
    def _secret(response: SecretResponse) -> JsonObject:
        return {
            "id": response.id,
            "project_id": response.project_id,
            "key": response.key,
            "description": response.description,
            "type": response.type,
            "metadata": response.metadata or {},
            "tags": list(response.tags),
            "archived": response.archived,
            "status": response.status,
        }

    @staticmethod
    def _secret_version(response: SecretVersionResponse) -> JsonObject:
        return {
            "id": response.id,
            "secret_id": response.secret_id,
            "value": response.value,
            "version": response.version,
            "active": response.active,
            "created_at": response.created_at,
        }

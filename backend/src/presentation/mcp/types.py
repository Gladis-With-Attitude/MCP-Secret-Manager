from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

type JsonValue = str | int | float | bool | None | Mapping[str, JsonValue] | Sequence[JsonValue]
type JsonObject = Mapping[str, JsonValue]


@dataclass(frozen=True, slots=True)
class McpAuthContext:
    api_key: str
    ip_address: str | None = None
    user_agent: str | None = None
    request_id: str | None = None
    transport: str = "stdio"


@dataclass(frozen=True, slots=True)
class McpToolDefinition:
    name: str
    description: str
    input_schema: JsonObject


@dataclass(frozen=True, slots=True)
class McpToolResult:
    content: JsonValue


class McpError(RuntimeError):
    def __init__(
        self,
        message: str,
        error_code: int = -32000,
        app_code: str = "mcp_error",
    ) -> None:
        super().__init__(message)
        self.error_code = error_code
        self.app_code = app_code


class McpAuthenticationError(McpError):
    def __init__(self, message: str = "Authentication failed.") -> None:
        super().__init__(message, error_code=-32001, app_code="authentication_failed")


class McpAuthorizationError(McpError):
    def __init__(self, message: str = "Permission denied.") -> None:
        super().__init__(message, error_code=-32003, app_code="permission_denied")


class McpToolNotFoundError(McpError):
    def __init__(self, tool_name: str) -> None:
        super().__init__(
            f"MCP tool not found: {tool_name}.",
            error_code=-32602,
            app_code="tool_not_found",
        )


class McpValidationError(McpError):
    def __init__(self, message: str) -> None:
        super().__init__(message, error_code=-32602, app_code="invalid_arguments")

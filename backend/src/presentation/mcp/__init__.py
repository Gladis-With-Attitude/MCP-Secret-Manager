"""MCP adapter package."""

from presentation.mcp.server import McpServer
from presentation.mcp.tools import SecretManagerMcpTools
from presentation.mcp.types import (
    JsonObject,
    JsonValue,
    McpAuthContext,
    McpError,
    McpToolDefinition,
    McpToolResult,
)

__all__ = [
    "JsonObject",
    "JsonValue",
    "McpAuthContext",
    "McpError",
    "McpServer",
    "McpToolDefinition",
    "McpToolResult",
    "SecretManagerMcpTools",
]

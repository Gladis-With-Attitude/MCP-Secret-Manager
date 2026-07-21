from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping

from presentation.mcp.types import (
    JsonObject,
    JsonValue,
    McpAuthContext,
    McpError,
    McpToolDefinition,
    McpToolNotFoundError,
    McpToolResult,
)

McpToolHandler = Callable[[Mapping[str, JsonValue], McpAuthContext], Awaitable[McpToolResult]]


class McpServer:
    def __init__(self, name: str, version: str = "0.1.0") -> None:
        self._name = name
        self._version = version
        self._definitions: dict[str, McpToolDefinition] = {}
        self._handlers: dict[str, McpToolHandler] = {}

    def register_tool(
        self,
        definition: McpToolDefinition,
        handler: McpToolHandler,
    ) -> None:
        self._definitions[definition.name] = definition
        self._handlers[definition.name] = handler

    def list_tools(self) -> tuple[McpToolDefinition, ...]:
        return tuple(self._definitions[name] for name in sorted(self._definitions))

    async def call_tool(
        self,
        name: str,
        arguments: Mapping[str, JsonValue],
        auth_context: McpAuthContext,
    ) -> McpToolResult:
        handler = self._handlers.get(name)
        if handler is None:
            raise McpToolNotFoundError(name)
        return await handler(arguments, auth_context)

    async def handle_json_rpc(
        self,
        message: JsonObject,
        auth_context: McpAuthContext,
    ) -> JsonObject:
        request_id = message.get("id")
        method = message.get("method")
        try:
            if method == "initialize":
                result: JsonValue = {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {"name": self._name, "version": self._version},
                    "capabilities": {"tools": {}},
                }
            elif method == "tools/list":
                result = {
                    "tools": [
                        {
                            "name": tool.name,
                            "description": tool.description,
                            "inputSchema": tool.input_schema,
                        }
                        for tool in self.list_tools()
                    ]
                }
            elif method == "tools/call":
                params = self._expect_object(message.get("params"), "params")
                tool_name = self._expect_string(params.get("name"), "name")
                arguments = self._expect_object(params.get("arguments") or {}, "arguments")
                tool_result = await self.call_tool(tool_name, arguments, auth_context)
                result = {"content": [{"type": "json", "json": tool_result.content}]}
            else:
                raise McpError(
                    "Unsupported MCP method.",
                    error_code=-32601,
                    app_code="method_not_found",
                )
            return {"jsonrpc": "2.0", "id": request_id, "result": result}
        except McpError as exc:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": exc.error_code,
                    "message": str(exc),
                    "data": {"code": exc.app_code},
                },
            }

    @staticmethod
    def _expect_object(value: JsonValue, field_name: str) -> JsonObject:
        if isinstance(value, Mapping):
            return value
        raise McpError(
            f"MCP field '{field_name}' must be an object.",
            error_code=-32600,
            app_code="invalid_request",
        )

    @staticmethod
    def _expect_string(value: JsonValue, field_name: str) -> str:
        if isinstance(value, str) and value.strip() != "":
            return value
        raise McpError(
            f"MCP field '{field_name}' must be a non-empty string.",
            error_code=-32600,
            app_code="invalid_request",
        )

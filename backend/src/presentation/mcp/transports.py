from __future__ import annotations

from typing import Literal, Protocol

from presentation.mcp.types import JsonObject

type McpTransportName = Literal["stdio", "http", "websocket"]


class McpTransport(Protocol):
    async def receive(self) -> JsonObject: ...

    async def send(self, message: JsonObject) -> None: ...

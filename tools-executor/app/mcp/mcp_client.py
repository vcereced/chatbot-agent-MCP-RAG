import time

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

from shared.domain.toolcall import ToolCall
from shared.domain.tooldefinition import ToolDefinition
from shared.domain.toolresult import ToolResult
from shared.errors.errors import MCPConnectionError
from app.mcp.mcp_adapter import MCPAdapter
from shared.logging.logger import configure_logging

logger = configure_logging(__name__)


class MCPClient:

    def __init__(self, name: str, url: str):
        self.name = name
        self.url = url

        self._http_context = None
        self._session_context = None

        self.read = None
        self.write = None
        self.session: ClientSession | None = None

    async def connect(self) -> None:

        logger.info("Connecting to MCP '%s' at %s", self.name, self.url)
        try:
            self._http_context = streamable_http_client(
                self.url
            )

            self.read, self.write = (
                await self._http_context.__aenter__()
            )

            self._session_context = ClientSession(
                self.read,
                self.write,
            )

            self.session = (
                await self._session_context.__aenter__()
            )

            await self.session.initialize()

        except Exception as exc:
            logger.error("Failed to connect to MCP '%s': %s", self.name, exc)
            await self.close()

            raise MCPConnectionError(
                f"No se pudo conectar al MCP "
                f"'{self.name}': {exc}"
            ) from exc

    async def list_tools(self) -> list[ToolDefinition]:

        logger.info("listing tools to MCP '%s' at %s", self.name, self.url)
        if self.session is None:
            raise MCPConnectionError(
                f"MCP '{self.name}' no está conectado"
            )

        try:
            result = await self.session.list_tools()

            return MCPAdapter.to_tool_definitions(
                result.tools
            )

        except Exception as exc:
            logger.error("listing tool failed on MCP '%s'", self.name)
            raise MCPConnectionError(
                f"Error obteniendo las herramientas "
                f"del MCP '{self.name}': {exc}"
            ) from exc

    async def call_tool(
        self,
        tool_call: ToolCall,
    ) -> ToolResult:

        logger.info(
            "Calling tool '%s' on MCP '%s'",
            tool_call.name,
            self.name,
        )

        if self.session is None:
            logger.error(
                "Tool '%s' failed: MCP '%s' is not connected",
                tool_call.name,
                self.name,
            )

            return ToolResult(
                tool_name=tool_call.name,
                success=False,
                error=f"MCP '{self.name}' no está conectado",
            )

        try:

            result = await self.session.call_tool(
                name=tool_call.name,
                arguments=tool_call.arguments,
            )

            return MCPAdapter.to_tool_result(
                tool_name=tool_call.name,
                result=result,
            )

        except Exception as exc:

            logger.error(
                "Tool '%s' failed on MCP '%s': %s",
                tool_call.name,
                self.name,
                exc,
                exc_info=True,
            )

            return ToolResult(
                tool_name=tool_call.name,
                success=False,
                error=str(exc),
            )

    async def close(self) -> None:
        logger.info("Closing MCP '%s'", self.name)

        if self._session_context is not None:
            try:
                await self._session_context.__aexit__(
                    None,
                    None,
                    None,
                )
            finally:
                self._session_context = None
                self.session = None

        if self._http_context is not None:
            try:
                await self._http_context.__aexit__(
                    None,
                    None,
                    None,
                )
            finally:
                self._http_context = None
                self.read = None
                self.write = None
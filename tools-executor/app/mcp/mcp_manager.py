from shared.domain.tooldefinition import ToolDefinition
from app.mcp.mcp_client import MCPClient
from shared.errors.errors import MCPConnectionError
from shared.logging.logger import configure_logging
from app.config import settings as configs
from app.config import MCPConfig


logger = configure_logging(__name__)


class MCPManager:

    def __init__(self, mcp_servers: list[MCPConfig]):
        self._clients: dict[str, MCPClient] = {}
        self._tool_clients: dict[str, MCPClient] = {}
        self._tool_definitions: list[ToolDefinition] = []

        for config in mcp_servers:
            self.register(
                MCPClient(
                    name=config.name,
                    url=config.url,
                )
            )

    def register(self, client: MCPClient) -> None:

        if client.name in self._clients:
            raise ValueError(
                f"Ya existe un MCP registrado con el nombre "
                f"'{client.name}'"
            )

        self._clients[client.name] = client

        logger.info(
            "MCP '%s' registrado",
            client.name,
        )

    def get(self, name: str) -> MCPClient | None:
        return self._clients.get(name)

    async def connect_all(self) -> None:

        for client in self._clients.values():

            try:
                await client.connect()

                tools = await client.list_tools()

                for tool in tools:
                    self._tool_clients[tool.name] = client

                self._tool_definitions.extend(tools)

                logger.info(
                    "MCP '%s' conectado con %d herramientas",
                    client.name,
                    len(tools),
                )

            except MCPConnectionError as exc:

                logger.error(
                    "No se pudo conectar al MCP '%s': %s",
                    client.name,
                    exc,
                )

    def get_client_for_tool(
        self,
        tool_name: str,
    ) -> MCPClient | None:

        return self._tool_clients.get(tool_name)

    def get_definitions(self) -> list[ToolDefinition]:

        return self._tool_definitions.copy()

    async def close_all(self) -> None:

        for client in self._clients.values():

            try:
                await client.close()

                logger.info(
                    "MCP '%s' cerrado",
                    client.name,
                )

            except Exception as exc:

                logger.error(
                    "Error cerrando MCP '%s': %s",
                    client.name,
                    exc,
                )
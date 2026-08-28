
from shared.domain.toolcall import ToolCall
from shared.domain.tooldefinition import ToolDefinition
from shared.domain.toolresult import ToolResult
from shared.logging.logger import configure_logging
from app.registry.tool_registry import ToolRegistry
from app.mcp.mcp_manager import MCPManager

logger = configure_logging(__name__)


class ToolManager:

    def __init__(
        self,
        registry: ToolRegistry,
        mcp_manager: MCPManager,
    ):
        self._registry = registry
        self._mcp_manager = mcp_manager

    def get_definitions(self) -> list[ToolDefinition]:
        """Devuelve todas las herramientas locales y MCP."""

        local_tools = self._registry.get_definitions()

        mcp_tools = self._mcp_manager.get_definitions()

        return local_tools + mcp_tools

    async def execute(
        self,
        tool_call: ToolCall,
    ) -> ToolResult:

        # 1. Intentamos encontrar una herramienta local
        local_tool = self._registry.get(tool_call.name)

        if local_tool is not None:

            logger.info(
                "Ejecutando herramienta local '%s'",
                tool_call.name,
            )

            result = await local_tool.execute(
            tool_call.arguments
        )

            return ToolResult(
                tool_name=tool_call.name,
                success=True,
                result=result,
            )

        # 2. Si no existe localmente, buscamos en MCP
        mcp_client = self._mcp_manager.get_client_for_tool(
            tool_call.name
        )

        if mcp_client is not None:

            logger.info(
                "Ejecutando herramienta MCP '%s'",
                tool_call.name,
            )

            return await mcp_client.call_tool(
                tool_call
            )

        # 3. No existe
        logger.warning(
            "Herramienta '%s' no encontrada",
            tool_call.name,
        )

        return ToolResult(
            tool_name=tool_call.name,
            success=False,
            error=f"Herramienta '{tool_call.name}' no encontrada",
        )
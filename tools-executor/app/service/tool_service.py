import asyncio
import logging
import time

from shared.domain.toolcall import ToolCall
from shared.domain.tooldefinition import ToolDefinition
from shared.domain.toolresult import ToolResult
from app.manager.tool_manager import ToolManager
from app.config import settings


logger = logging.getLogger(__name__)


class ToolService:

    def __init__(self, tool_manager: ToolManager):
        self.tool_manager = tool_manager

    async def execute(self, toolcall: ToolCall) -> ToolResult:

        logger.info(
            "Executing tool: %s with arguments: %s",
            toolcall.name,
            toolcall.arguments,
        )

        start_time = time.perf_counter()

        try:

            result = await asyncio.wait_for(
                self.tool_manager.execute(toolcall),
                timeout=settings.tool_timeout_seconds,
            )

            elapsed_ms = round(
                (time.perf_counter() - start_time) * 1000,
                2,
            )

            logger.info(
                "Tool '%s' executed successfully in %sms",
                toolcall.name,
                elapsed_ms,
            )

            # El ToolManager ya devuelve ToolResult.
            result.execution_time_ms = elapsed_ms

            return result

        except asyncio.TimeoutError:

            elapsed_ms = round(
                (time.perf_counter() - start_time) * 1000,
                2,
            )

            logger.error(
                "Tool '%s' timed out after %s seconds",
                toolcall.name,
                settings.tool_timeout_seconds,
            )

            return ToolResult(
                tool_name=toolcall.name,
                success=False,
                error="Execution timed out.",
                execution_time_ms=elapsed_ms,
            )

        except Exception as exc:

            elapsed_ms = round(
                (time.perf_counter() - start_time) * 1000,
                2,
            )

            logger.error(
                "Error executing tool '%s': %s",
                toolcall.name,
                exc,
                exc_info=True,
            )

            return ToolResult(
                tool_name=toolcall.name,
                success=False,
                error=f"Execution failed: {exc}",
                execution_time_ms=elapsed_ms,
            )

    def list_tools(self) -> list[ToolDefinition]:

        logger.info("Listing available tools")

        tools = self.tool_manager.get_definitions()

        logger.info(
            "Available tools: %d",
            len(tools),
        )

        return tools
import asyncio
import time

from shared.domain.toolcall import ToolCall
from shared.domain.tooldefinition import ToolDefinition
from shared.domain.toolresult import ToolResult
from app.manager.tool_manager import ToolManager
from app.config import settings
from shared.logging.logger import configure_logging


logger = configure_logging(__name__)


class ToolService:

    def __init__(self, tool_manager: ToolManager):
        self.tool_manager = tool_manager

    async def execute(self, toolcall: ToolCall) -> ToolResult:

        logger.info(
            "Tool execution started name=%s",
            toolcall.name,
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
                "Tool execution completed name=%s success=%s duration_ms=%.2f",
                toolcall.name,
                result.success,
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
                "Tool execution timed out name=%s timeout_seconds=%s duration_ms=%.2f",
                toolcall.name,
                settings.tool_timeout_seconds,
                elapsed_ms,
            )

            return ToolResult(
                tool_name=toolcall.name,
                success=False,
                error="Execution timed out.",
                execution_time_ms=elapsed_ms,
            )

        except Exception:

            elapsed_ms = round(
                (time.perf_counter() - start_time) * 1000,
                2,
            )

            logger.error(
                "Tool execution failed name=%s duration_ms=%.2f",
                toolcall.name,
                elapsed_ms,
                exc_info=True,
            )

            return ToolResult(
                tool_name=toolcall.name,
                success=False,
                error="Execution failed.",
                execution_time_ms=elapsed_ms,
            )

    def list_tools(self) -> list[ToolDefinition]:

        tools = self.tool_manager.get_definitions()
        return tools
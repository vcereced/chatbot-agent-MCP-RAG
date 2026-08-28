from mcp import types
from shared.domain.tooldefinition import (
    ToolDefinition,
    ParameterDefinition,
    PropertyDefinition,
)
from shared.domain.toolresult import ToolResult


class MCPAdapter:

    @staticmethod
    def to_tool_definition(tool: types.Tool) -> ToolDefinition:
        schema = tool.input_schema

        properties = {
            name: PropertyDefinition(
                type=definition["type"],
                description=definition.get("description"),
            )
            for name, definition in schema.get("properties", {}).items()
        }

        return ToolDefinition(
            name=tool.name,
            description=tool.description or "",
            input_schema=ParameterDefinition(
                properties=properties,
                required=schema.get("required", []),
            ),
        )
    @staticmethod
    def to_tool_definitions(tools: list[types.Tool]) -> list[ToolDefinition]:

        return [
            MCPAdapter.to_tool_definition(tool)
            for tool in tools
        ]

    @staticmethod
    def to_tool_result(
        tool_name: str,
        result: types.CallToolResult,
        execution_time_ms: float | None = None,
    ) -> ToolResult:

        content = "\n".join(
            item.text
            for item in result.content
            if isinstance(item, types.TextContent)
        )

        return ToolResult(
            tool_name=tool_name,
            success=not result.is_error,
            result=content,
            execution_time_ms=execution_time_ms,
        )
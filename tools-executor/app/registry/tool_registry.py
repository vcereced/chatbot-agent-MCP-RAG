from app.tools.base import BaseTool
from shared.domain.tooldefinition import ToolDefinition


class ToolRegistry:

    def __init__(self):
        self._tools: dict[str, BaseTool] = {}

    def register(self, tool: BaseTool) -> None:

        definition = tool.get_definition()

        if definition.name in self._tools:
            raise ValueError(
                f"Ya existe una herramienta registrada "
                f"con el nombre '{definition.name}'"
            )

        self._tools[definition.name] = tool

    def get(self, name: str) -> BaseTool | None:
        return self._tools.get(name)

    def get_definitions(self) -> list[ToolDefinition]:
        return [
            tool.get_definition()
            for tool in self._tools.values()
        ]
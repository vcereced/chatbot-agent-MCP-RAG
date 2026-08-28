from pathlib import Path
from typing import Any

from app.tools.base_tool import BaseTool

from shared.domain.tooldefinition import (
    ToolDefinition,
    ParameterDefinition,
    PropertyDefinition,
)


class DirectoryTreeTool(BaseTool):

    def get_definition(self) -> ToolDefinition:

        return ToolDefinition(
            name="directory_tree",
            description="Returns the directory tree of a given path.",
            input_schema=ParameterDefinition(
                type="object",
                properties={
                    "path": PropertyDefinition(
                        type="string",
                        description="Directory path to inspect.",
                    ),
                },
                required=["path"],
            ),
        )

    async def execute(self, arguments: dict[str, Any]) -> object:

        path = Path(arguments["path"])

        if not path.exists():
            raise ValueError(f"Path '{path}' does not exist.")

        if not path.is_dir():
            raise ValueError(f"'{path}' is not a directory.")

        return self._build_tree(path)

    def _build_tree(self, directory: Path) -> list[dict]:

        tree = []

        for entry in sorted(directory.iterdir(), key=lambda p: (p.is_file(), p.name.lower())):

            node = {
                "name": entry.name,
                "type": "directory" if entry.is_dir() else "file",
            }

            if entry.is_dir():
                node["children"] = self._build_tree(entry)

            tree.append(node)

        return tree
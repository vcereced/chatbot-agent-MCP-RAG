from mcp.server import Server
from mcp import types

from app.services.filesystem_service import FilesystemService


filesystem_service = FilesystemService()


async def list_tools(
    context,
    params,
) -> types.ListToolsResult:

    return types.ListToolsResult(
        tools=[
            types.Tool(
                name="list_directory",
                description="Lista los archivos y directorios de una ruta.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Ruta del directorio a listar.",
                        }
                    },
                },
            ),
            types.Tool(
                name="read_file",
                description="Lee el contenido de un archivo.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Ruta del archivo a leer.",
                        }
                    },
                    "required": ["path"],
                },
            ),
        ]
    )


async def call_tool(
    context,
    params: types.CallToolRequestParams,
) -> types.CallToolResult:

    try:

        if params.name == "list_directory":

            path = params.arguments.get("path", ".")

            result = filesystem_service.list_directory(path)

            return types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text="\n".join(result),
                    )
                ]
            )

        if params.name == "read_file":

            path = params.arguments["path"]

            result = filesystem_service.read_file(path)

            return types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text=result,
                    )
                ]
            )

        return types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text=f"Tool desconocida: {params.name}",
                )
            ],
            isError=True,
        )

    except (ValueError, KeyError) as e:

        return types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text=str(e),
                )
            ],
            isError=True,
        )


server = Server(
    "filesystem",
    version="1.0.0",
    on_list_tools=list_tools,
    on_call_tool=call_tool,
)
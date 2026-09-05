import httpx
import pytest
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


MCP_FILESYSTEM_URL = "http://mcp-filesystem:8000/mcp"


def test_mcp_filesystem_health():
    response = httpx.get("http://mcp-filesystem:8000/health")

    response.raise_for_status()
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_mcp_filesystem_lists_and_reads_files():
    async with streamable_http_client(MCP_FILESYSTEM_URL) as (
        read_stream,
        write_stream,
    ):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            tools = await session.list_tools()
            tool_names = {tool.name for tool in tools.tools}
            assert {"list_directory", "read_file"} <= tool_names

            result = await session.call_tool(
                "read_file",
                {"path": "hello.txt"},
            )

            assert result.is_error is not True
            assert "hola desde el archivo hello.txt" in result.content[0].text
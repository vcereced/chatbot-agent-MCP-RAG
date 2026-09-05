import httpx


TOOLS_EXECUTOR_URL = "http://tools-executor:8000"


def execute_tool(name: str, arguments: dict[str, object]) -> dict:
    response = httpx.post(
        f"{TOOLS_EXECUTOR_URL}/execute",
        json={
            "tool_call": {
                "name": name,
                "arguments": arguments,
            }
        },
    )
    response.raise_for_status()
    return response.json()["tool_result"]


def test_list_tools_includes_local_and_mcp_tools():
    response = httpx.get(f"{TOOLS_EXECUTOR_URL}/tools")

    response.raise_for_status()
    tool_names = {tool["name"] for tool in response.json()["tools"]}

    assert {"calculator", "datetime", "list_directory", "read_file"} <= tool_names


def test_execute_calculator_tool():
    result = execute_tool(
        "calculator",
        {"expression": "2 + 3 * 4"},
    )

    assert result["tool_name"] == "calculator"
    assert result["success"] is True
    assert result["result"] == 14
    assert result["execution_time_ms"] is not None


def test_execute_filesystem_mcp_tool():
    result = execute_tool(
        "read_file",
        {"path": "hello.txt"},
    )

    assert result["tool_name"] == "read_file"
    assert result["success"] is True
    assert "hola desde el archivo hello.txt" in result["result"]


def test_execute_unknown_tool_returns_error_result():
    result = execute_tool("unknown_tool", {})

    assert result["tool_name"] == "unknown_tool"
    assert result["success"] is False
    assert result["error"] == "Herramienta 'unknown_tool' no encontrada"
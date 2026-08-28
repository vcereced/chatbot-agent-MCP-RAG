from app.clients.base_client import BaseClient
from app.config import config
from shared.tools.execute import ExecuteToolRequest, ExecuteToolResponse
from shared.logging.logger import configure_logging
from shared.domain.toolcall import ToolCall
from shared.domain.toolresult import ToolResult
from shared.domain.tooldefinition import ToolDefinition
from shared.tools.list_tools import ListToolsResponse


logger = configure_logging(__name__)

class ToolsClient(BaseClient):

    def __init__(self):
        super().__init__()
        self._tools = None     

    async def execute(self, tool_call: ToolCall) -> ToolResult:

        logger.info(f"Sending request to tool-executor: {tool_call.name}    with arguments: {tool_call.arguments}   ")
        response = await self.post(
            f"{config.TOOLS_URL}/execute",
            ExecuteToolRequest(tool_call=tool_call),
            ExecuteToolResponse,
        )

        return response.tool_result

    async def list_tools(self) -> list[ToolDefinition]:

        if self._tools is None:
            await self.load_tools()
        return self._tools

    async def load_tools(self):
    
        response = await self.get(f"{config.TOOLS_URL}/tools", ListToolsResponse)
        self._tools = response.tools
    

    

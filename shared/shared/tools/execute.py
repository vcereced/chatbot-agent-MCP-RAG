from pydantic import BaseModel
from shared.domain.toolcall import ToolCall
from shared.domain.toolresult import ToolResult


class ExecuteToolRequest(BaseModel):

    tool_call : ToolCall


class ExecuteToolResponse(BaseModel):

    tool_result: ToolResult
from pydantic import BaseModel


class ToolResult(BaseModel):

    tool_name: str
    success: bool = True
    result: object | None = None
    error: str | None = None
    execution_time_ms: float | None = None
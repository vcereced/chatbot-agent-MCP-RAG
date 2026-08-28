from pydantic import BaseModel
from shared.domain.toolcall import ToolCall

class GenerateResult(BaseModel):

    text: str | None = None

    tool_call: ToolCall | None = None
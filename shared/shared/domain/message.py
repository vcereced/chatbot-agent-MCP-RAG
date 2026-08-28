from pydantic import BaseModel
from shared.domain.toolcall import ToolCall
from typing import Literal

class Message(BaseModel):

    role: Literal[
        "system",
        "user",
        "assistant",
        "tool"
    ]

    content: str | None = None

    tool_call: ToolCall | None = None

    tool_name: str | None = None
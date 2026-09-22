from pydantic import BaseModel

class ToolCall(BaseModel):

    name: str

    arguments: dict[str, object]

    thought_signature: str | None = None
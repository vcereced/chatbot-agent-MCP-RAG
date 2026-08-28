from pydantic import BaseModel
from shared.domain.message import Message
from shared.domain.generate_result import GenerateResult
from shared.domain.tooldefinition import ToolDefinition
from shared.domain.conversation import Conversation

class GenerateRequest(BaseModel):
    messages: list[Message]
    
    tools: list[ToolDefinition] | None


class GenerateResponse(BaseModel):
    result: GenerateResult
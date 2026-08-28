from pydantic import BaseModel
from shared.domain.tooldefinition import ToolDefinition

class ListToolsResponse(BaseModel):
    tools: list[ToolDefinition]
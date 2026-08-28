from app.clients.base_client import BaseClient
from app.config import config
from shared.llm.generate import GenerateRequest, GenerateResponse
from shared.logging.logger import configure_logging
from shared.domain.conversation import Conversation
from shared.llm.generate import GenerateResult
from shared.domain.tooldefinition import ToolDefinition

logger = configure_logging(__name__)

class LLMClient(BaseClient):

    async def generate(self, conversation: Conversation, tools: list[ToolDefinition] | None = None) -> GenerateResult:


        request = GenerateRequest(messages=conversation.messages, tools=tools)
        response = await self.post(f"{config.LLM_URL}/generate", request, GenerateResponse)
        logger.info("Received response from LLM service: %s", response.result)

        return GenerateResult(text=response.result.text, tool_call=response.result.tool_call)

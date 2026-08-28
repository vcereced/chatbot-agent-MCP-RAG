from app.clients.base_client import BaseClient
from shared.domain.conversation import Conversation
from app.config import config
from shared.memory.conversation import GetOrCreateConversationRequest, GetOrCreateConversationResponse, SaveConversationRequest, SaveConversationResponse
from uuid import uuid4
from shared.logging.logger import configure_logging

logger = configure_logging(__name__)


class MemoryClient(BaseClient):

    async def get(self, conversation_id: str | None ) -> Conversation:
    
        response = await self.post(
            f"{config.MEMORY_URL}/conversations/get_or_create",
            GetOrCreateConversationRequest(
                conversation_id=conversation_id,
            ),
            GetOrCreateConversationResponse,
        )

        return response.conversation

    
    async def save(
        self,
        conversation: Conversation,
    ) -> None:

        await self.post(
            f"{config.MEMORY_URL}/conversations/save",
            SaveConversationRequest(
                conversation=conversation,
            ),
            SaveConversationResponse,
        )

    async def get_or_create(self, conversation_id: str | None) -> Conversation:
        return await self.get(conversation_id)

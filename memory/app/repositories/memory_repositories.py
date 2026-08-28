from shared.domain.conversation import Conversation
from shared.logging.logger import configure_logging

logger = configure_logging(__name__)


class MemoryRepository:

    def __init__(self) -> None:
        self._storage: dict[str, Conversation] = {}

    async def get(self, conversation_id: str) -> Conversation | None:
        return self._storage.get(conversation_id)

    async def save(self, conversation: Conversation) -> bool:
        self._storage[conversation.id] = conversation.model_copy(deep=True)
        return True
from shared.domain.conversation import Conversation
from shared.logging.logger import configure_logging
from app.repositories.memory_repositories import MemoryRepository
from shared.errors.errors import MemoryStorageError
from uuid import uuid4

logger = configure_logging(__name__)


class MemoryService:

    def __init__(self) -> None:

        self.repository = MemoryRepository()

    async def get_or_create(self, conversation_id: str | None) -> Conversation:
        try:
            if conversation_id:
                logger.info(f"Retrieving conversation with ID: {conversation_id}")
                conversation = await self.repository.get(conversation_id)
                if conversation:
                    return conversation
                logger.info(f"Conversation {conversation_id} not found. Creating a new one.")
                new_id = conversation_id
            else:
                new_id = str(uuid4())
                logger.info(f"Generating new conversation ID: {new_id}")

            conversation = Conversation(id=new_id, messages=[])
            await self.repository.save(conversation)
            return conversation

        except Exception as e:
            logger.error(f"Error in get_or_create for ID '{conversation_id}': {str(e)}", exc_info=True)
            raise MemoryStorageError(f"Failed to retrieve or create conversation: {str(e)}") from e

    async def save(self, conversation: Conversation) -> bool:
        try:
            logger.info(f"Saving conversation with ID: {conversation.id}")
            # ¡AQUÍ ESTÁ LA CORRECCIÓN! Le pasamos 'conversation' al repositorio
            return await self.repository.save(conversation)
        except Exception as e:
            logger.error(f"Error saving conversation '{conversation.id}': {str(e)}", exc_info=True)
            raise MemoryStorageError(f"Failed to save conversation: {str(e)}") from e
        
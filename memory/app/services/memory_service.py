from shared.domain.conversation import Conversation
from app.repositories.memory_repositories import MemoryRepository
from shared.errors.errors import MemoryStorageError
from uuid import uuid4

class MemoryService:

    def __init__(self) -> None:

        self.repository = MemoryRepository()

    async def get_or_create(self, conversation_id: str | None) -> Conversation:
        try:
            if conversation_id:
                conversation = await self.repository.get(conversation_id)
                if conversation:
                    return conversation
                new_id = conversation_id
            else:
                new_id = str(uuid4())

            conversation = Conversation(id=new_id, messages=[])
            await self.repository.save(conversation)
            return conversation

        except Exception as e:
            raise MemoryStorageError("Failed to retrieve or create conversation") from e

    async def save(self, conversation: Conversation) -> bool:
        try:
            # ¡AQUÍ ESTÁ LA CORRECCIÓN! Le pasamos 'conversation' al repositorio
            return await self.repository.save(conversation)
        except Exception as e:
            raise MemoryStorageError("Failed to save conversation") from e
        
from fastapi import APIRouter, HTTPException, status
from app.services.memory_service import MemoryService
from shared.memory.conversation import GetOrCreateConversationRequest, GetOrCreateConversationResponse, SaveConversationRequest, SaveConversationResponse
from shared.logging.logger import configure_logging
from shared.errors.errors import MemoryStorageError

logger = configure_logging(__name__)

router = APIRouter()

service = MemoryService()

@router.post("/conversations/get_or_create", response_model=GetOrCreateConversationResponse,)
async def get_conversation(request: GetOrCreateConversationRequest) -> GetOrCreateConversationResponse:
    logger.info("Get or create conversation requested conversation_id=%s", request.conversation_id)
    try:
        conversation = await service.get_or_create(request.conversation_id)
        logger.info("Conversation ready conversation_id=%s", conversation.id)
        return GetOrCreateConversationResponse(conversation=conversation)
    except MemoryStorageError as e:
        # Fallo de la base de datos/persistencia
        logger.warning("Memory storage unavailable during get_or_create: %s", e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail="Memory storage unavailable."
        )
    except Exception:
        # Cualquier otro fallo inesperado
        logger.exception("Unexpected error in get_or_create")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno en el servicio de memoria."
        )

@router.post("/conversations/save", response_model= SaveConversationResponse)
async def save(request: SaveConversationRequest)-> SaveConversationResponse:
    logger.info("Save conversation requested conversation_id=%s", request.conversation.id)
    try:
        success = await service.save(request.conversation)
        logger.info("Conversation save completed conversation_id=%s success=%s", request.conversation.id, success)
        return SaveConversationResponse(success=success)
    except MemoryStorageError as e:
        logger.warning("Memory storage unavailable during save: %s", e)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail="Memory storage unavailable."
        )
    except Exception:
        logger.exception("Unexpected error saving conversation")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al guardar la conversación."
        )


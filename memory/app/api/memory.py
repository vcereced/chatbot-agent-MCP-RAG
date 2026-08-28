from fastapi import APIRouter
from app.services.memory_service import MemoryService
from shared.memory.conversation import GetOrCreateConversationRequest, GetOrCreateConversationResponse, SaveConversationRequest, SaveConversationResponse
from shared.logging.logger import configure_logging
from shared.errors.errors import MemoryStorageError

logger = configure_logging(__name__)

router = APIRouter()

service = MemoryService()

@router.post("/conversations/get_or_create", response_model=GetOrCreateConversationResponse,)
async def get_conversation(request: GetOrCreateConversationRequest) -> GetOrCreateConversationResponse:
    logger.info(f"/conversations/get con el id {request.conversation_id}")
    try:
        conversation = await service.get_or_create(request.conversation_id)
        return GetOrCreateConversationResponse(conversation=conversation)
    except MemoryStorageError as e:
        # Fallo de la base de datos/persistencia
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail=str(e)
        )
    except Exception as e:
        # Cualquier otro fallo inesperado
        logger.critical(f"Error no controlado en /get_or_create: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno en el servicio de memoria."
        )

@router.post("/conversations/save", response_model= SaveConversationResponse)
async def save(request: SaveConversationRequest)-> SaveConversationResponse:
    logger.info(f"POST /conversations/save for ID: {request.conversation.id}")
    try:
        success = await service.save(request.conversation)
        return SaveConversationResponse(success=success)
    except MemoryStorageError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail=str(e)
        )
    except Exception as e:
        logger.critical(f"Error no controlado en /save: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno al guardar la conversación."
        )


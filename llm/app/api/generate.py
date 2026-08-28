import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas import GenerateRequest, GenerateResponse
from app.services.llm_service import LLMService
from shared.logging.logger import configure_logging

logger = configure_logging(__name__)

router = APIRouter(tags=["LLM Generation"])


def get_llm_service() -> LLMService:
    return LLMService()


@router.post(
    "/generate", 
    response_model=GenerateResponse,
    status_code=status.HTTP_200_OK
)
async def generate(
    request: GenerateRequest,
    service: LLMService = Depends(get_llm_service)
) -> GenerateResponse:
    
    logger.info("Recibida petición /generate")
    
    try:
        result = await service.generate(request.messages, request.tools)
        return GenerateResponse(result=result)

    except httpx.ConnectError as e:
        logger.error(f"Cannot connect to Ollama: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cannot connect to LLM provider service."
        )

    except httpx.TimeoutException as e:
        logger.error(f"Ollama request timed out: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="LLM provider request timed out."
        )

    except httpx.HTTPStatusError as e:
        logger.error(f"Ollama HTTP error {e.response.status_code}: {e.response.text}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"LLM provider error: {e.response.text}"
        )

    except Exception as e:
        logger.critical(f"Unexpected error in /generate: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during LLM generation."
        )
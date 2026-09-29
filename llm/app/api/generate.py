import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from google.genai.errors import APIError as GoogleAPIError
from time import perf_counter
from app.schemas import GenerateRequest, GenerateResponse
from app.services.llm_service import LLMService
from shared.logging.logger import configure_logging

logger = configure_logging(__name__)

router = APIRouter(tags=["LLM Generation"])


def get_llm_service() -> LLMService:
    try:
        return LLMService()
    except ValueError as exc:
        logger.error("Invalid LLM provider configuration: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LLM provider is not configured correctly.",
        ) from exc


@router.post(
    "/generate", 
    response_model=GenerateResponse,
    status_code=status.HTTP_200_OK
)
async def generate(
    request: GenerateRequest,
    service: LLMService = Depends(get_llm_service)
) -> GenerateResponse:
    
    started_at = perf_counter()
    logger.info(
        "Generation request received messages=%d tools=%d",
        len(request.messages),
        len(request.tools or []),
    )

    try:
        result = await service.generate(request.messages, request.tools)
        logger.info(
            "Generation request completed duration_ms=%.2f result_type=%s",
            (perf_counter() - started_at) * 1000,
            "tool_call" if result.tool_call is not None else "text",
        )
        return GenerateResponse(result=result)

    except httpx.ConnectError:
        logger.exception("Cannot connect to LLM provider")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cannot connect to LLM provider service."
        )

    except httpx.TimeoutException:
        logger.exception("LLM provider request timed out")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="LLM provider request timed out."
        )

    except httpx.RequestError:
        logger.exception("Network error while contacting LLM provider")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Cannot communicate with LLM provider service.",
        )

    except GoogleAPIError as e:
        logger.exception("Google GenAI API request failed status_code=%s", e.code)
        if e.code == status.HTTP_429_TOO_MANY_REQUESTS:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Google GenAI quota or rate limit exceeded.",
            ) from e

        if e.code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Google GenAI authentication or permission check failed.",
            ) from e

        if e.code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Google GenAI model or endpoint was not found.",
            ) from e

        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Google GenAI provider returned an error.",
        ) from e

    except httpx.HTTPStatusError as e:
        logger.error(
            "LLM provider returned HTTP error status_code=%d",
            e.response.status_code,
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="LLM provider returned an error."
        )

    except Exception:
        logger.exception("Unexpected error during LLM generation")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during LLM generation."
        )
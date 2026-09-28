import httpx
from time import perf_counter
from shared.domain.tooldefinition import ToolDefinition
from shared.domain.message import Message
from shared.domain.generate_result import GenerateResult
from shared.logging.logger import configure_logging
from app.adapters.ollama_mapper import OllamaMapper
from fastapi import HTTPException
from app.config import config 
from app.providers.base_provider import BaseProvider

logger = configure_logging(__name__)

class OllamaProvider(BaseProvider):

    def __init__(self):

        self.model = config.OLLAMA_MODEL
        self.endpoint = config.OLLAMA_ENDPOINT
        self.client = httpx.AsyncClient(
            base_url = config.OLLAMA_BASE_URL,
            timeout = float(config.TIMEOUT),
        )

    async def generate(
        self,
        messages: list[Message] | None,
        tools: list[ToolDefinition] | None,
    ) -> GenerateResult:

        started_at = perf_counter()
        payload = {
            "model": self.model,
            "messages": OllamaMapper.to_messages(messages),
            "stream": False,
        }
        if tools:#si llegan tools se añaden al mensaje para el llm
            payload["tools"] = OllamaMapper.to_tools(tools)
        logger.info(
            "Sending request to Ollama model=%s messages=%d tools=%d",
            self.model,
            len(messages or []),
            len(tools or []),
        )

        try:
            response = await self.client.post(
                self.endpoint,
                json=payload,
            )
            response.raise_for_status()

        except httpx.ConnectError:
            raise HTTPException(
                status_code=503,
                detail="Cannot connect to Ollama."
            )

        except httpx.TimeoutException:
            raise HTTPException(
                status_code=504,
                detail="Ollama request timed out."
            )

        except httpx.HTTPStatusError as e:
            logger.error(
                "Ollama returned HTTP error status_code=%d",
                e.response.status_code,
            )
            raise HTTPException(
                status_code=e.response.status_code,
                detail="Ollama returned an error.",
            )

        result = OllamaMapper.to_generate_result(response.json())
        logger.info(
            "Ollama response received status_code=%d duration_ms=%.2f result_type=%s",
            response.status_code,
            (perf_counter() - started_at) * 1000,
            "tool_call" if result.tool_call is not None else "text",
        )
        return result

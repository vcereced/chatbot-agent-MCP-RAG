from shared.domain.message import Message
from shared.domain.generate_result import GenerateResult
from shared.domain.tooldefinition import ToolDefinition
from shared.logging.logger import configure_logging
from app.providers.ollama_provider import OllamaProvider

logger = configure_logging(__name__)


class LLMService:

    def __init__(self, provider: OllamaProvider | None = None) -> None:
        self.llm_provider = provider or OllamaProvider()

    async def generate(
        self, 
        messages: list[Message] | None, 
        tools: list[ToolDefinition] | None
    ) -> GenerateResult:
        
        logger.info(f"LLMService: procesando {len(messages) if messages else 0} mensajes.")
        
        # El servicio delega la ejecución al provider.
        # Si httpx falla, la excepción sube limpiamente hacia el Router.
        result = await self.llm_provider.generate(messages or [], tools)
        
        logger.debug(f"Resultado de LLMService: {result}")
        return result
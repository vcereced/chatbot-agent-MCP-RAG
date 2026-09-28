from shared.domain.message import Message
from shared.logging.logger import configure_logging
from app.runtime.emmiter import WebSocketEmitter

from app.clients.llm_client import LLMClient
from app.clients.tools_client import ToolsClient
from app.clients.memory_client import MemoryClient
from shared.domain.chatresult import ChatResult
from time import perf_counter

logger = configure_logging(__name__)
        

class ChatService:

    def __init__(self):

        self.memory = MemoryClient()
        self.llm = LLMClient()
        self.tools = ToolsClient()
        

    async def chat(
        self,
        conversation_id: str | None,
        message: str,
        emitter: WebSocketEmitter,
        run_id: str,
    ) -> ChatResult:

        n_iterations = 1
        n_tools = 0
        started_at = perf_counter()
        logger.info(
            "Chat processing started conversation_id=%s message_chars=%d",
            conversation_id,
            len(message),
        )
        logger.info("Loading conversation")
        await emitter.status(run_id, "Obteniendo conversacion")

        conversation = await self.memory.get_or_create(conversation_id)

        conversation.messages.append(
            Message(
                role="user",
                content=message,
            )
        )

        logger.info("Loading available tools")
        await emitter.status(run_id, "Obteniendo herramientas")
        tools = await self.tools.list_tools()
        logger.info("Available tools loaded count=%d", len(tools))

        logger.info("Requesting LLM response iteration=%d", n_iterations)
        await emitter.status(run_id, f"generando {n_iterations} interaccion con llm")
        result = await self.llm.generate(conversation, tools)

        max_iterations = 4

        for iteration in range(max_iterations):
            if result.tool_call is None:
                break
                # if sult.tool_call:

            # Guardar la llamada a la herramienta realizada por el LLM
            conversation.messages.append(
                Message(
                    role="assistant",
                    tool_call=result.tool_call,
                )
            )

            logger.info("Executing tool name=%s", result.tool_call.name)
            n_tools += 1 
            await emitter.status(run_id, f"ejecutando {n_tools} herramienta del agente")
            tool_result = await self.tools.execute(result.tool_call)

            logger.info(
                "Tool execution finished name=%s success=%s",
                tool_result.tool_name,
                tool_result.success,
            )

            # Guardar el resultado de la herramienta
            conversation.messages.append(
                Message(
                    role="tool",
                    tool_name=tool_result.tool_name,
                    content=str(tool_result.result),
                )
            )

            n_iterations += 1
            logger.info("Requesting LLM response iteration=%d", n_iterations)
            await emitter.status(run_id, f"generando {n_iterations} interaccion con llm")
            result = await self.llm.generate(conversation, tools)

        if result.tool_call is not None:
            logger.warning(
                "Tool iteration limit reached limit=%d tools_executed=%d",
                max_iterations,
                n_tools,
            )
            result.text = ("No he podido completar la consulta dentro del límite de operaciones permitido.")

        conversation.messages.append(
            Message(
                role="assistant",
                content=result.text,
            )
        )

        logger.info("Saving conversation conversation_id=%s", conversation.id)
        await emitter.status(run_id, "guardando conversacion")
        await self.memory.save(conversation)
        logger.info(
            "Chat processing completed conversation_id=%s tools_executed=%d iterations=%d duration_ms=%.2f",
            conversation.id,
            n_tools,
            n_iterations,
            (perf_counter() - started_at) * 1000,
        )
        return ChatResult(
            conversation_id=conversation.id,
            response=result.text,
        )
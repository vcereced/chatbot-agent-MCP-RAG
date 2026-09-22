from shared.agent.chat import ChatRequest, ChatResponse
from shared.llm.generate import GenerateRequest, GenerateResponse
from shared.domain.message import Message
from shared.domain.toolresult import ToolResult
from shared.logging.logger import configure_logging
from app.runtime.emmiter import WebSocketEmitter

from app.clients.llm_client import LLMClient
from app.clients.tools_client import ToolsClient
from app.clients.memory_client import MemoryClient
from shared.domain.chatresult import ChatResult
from shared.domain.tooldefinition import ToolDefinition

logger = configure_logging(__name__)
        

class ChatService:

    def __init__(self):

        self.memory = MemoryClient()
        self.llm = LLMClient()
        self.tools = ToolsClient()
        

    async def chat(self, conversation_id: str | None, message: str, emitter: WebSocketEmitter, run_id) -> ChatResult:

        n_iterations = 1
        n_tools = 0
        logger.info(f"Processing chat id: {conversation_id}, message: {message}")
        logger.info("obteniendo conversacion")
        await emitter.status(run_id, "Obteniendo conversacion")

        conversation = await self.memory.get_or_create(conversation_id)

        conversation.messages.append(
            Message(
                role="user",
                content=message,
            )
        )

        logger.info("Getting list of tools")
        await emitter.status(run_id, "Obteniendo herramientas")
        tools = await self.tools.list_tools()

        logger.info(f"Generating LLM response, {conversation}")
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

            logger.info(f"Executing tool {result.tool_call}")
            n_tools += 1 
            await emitter.status(run_id, f"ejecutando {n_tools} herramienta del agente")
            tool_result = await self.tools.execute(result.tool_call)

            logger.info(f"Executing tool {tool_result}")

            # Guardar el resultado de la herramienta
            conversation.messages.append(
                Message(
                    role="tool",
                    tool_name=tool_result.tool_name,
                    content=str(tool_result.result),
                )
            )

            logger.info("generating llm with tool")
            n_iterations += 1
            await emitter.status(run_id, f"generando {n_iterations} interaccion con llm")
            result = await self.llm.generate(conversation, tools)

        if result.tool_call is not None:
            result.text = ("No he podido completar la consulta dentro del límite de operaciones permitido.")

        conversation.messages.append(
            Message(
                role="assistant",
                content=result.text,
            )
        )

        logger.info("Saving conversation")
        await emitter.status(run_id, "guardando conversacion")
        await self.memory.save(conversation)
        logger.info(conversation)
        return ChatResult(
            conversation_id=conversation.id,
            response=result.text,
        )
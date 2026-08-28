import asyncio
import uuid
from shared.agent.chat import ChatRequest

from fastapi import WebSocket, WebSocketDisconnect

from app.runtime.run_manager import RunManager
from app.runtime.emmiter import WebSocketEmitter
from app.services.chat_service import ChatService
from shared.logging.logger import configure_logging

logger = configure_logging(__name__)


class WebSocketSession:

    def __init__(
        self,
        websocket: WebSocket,
        chat_service: ChatService,
    ):
        self.websocket = websocket
        self.chat_service = chat_service
        self.run_manager = RunManager()
        self.emitter = WebSocketEmitter(websocket)

    async def run(self):

        logger.info("WebSocket session started")

        try:

            while True:

                request = await self.websocket.receive_json()

                match request["type"]:

                    case "message":
                        await self._handle_message(request)

                    case "cancel":
                        await self._handle_cancel(request)

        except WebSocketDisconnect as e:
            logger.info(f"WebSocket disconnected: {e.code}")
            self.run_manager.cancel_all()

    async def _handle_message(self, request: ChatRequest):

        run_id = str(uuid.uuid4())

        logger.info("SEND started")
        await self.emitter.started(
            run_id,
            "started",
            request.get("conversation_id"),
        )

        task = asyncio.create_task(
            self.chat_service.chat(
                conversation_id=request.get("conversation_id"),
                message=request["message"],
                emitter=self.emitter,
                run_id=run_id,
            )
        )

        self.run_manager.add(run_id, task)

        logger.info("CREATING TASK")
        asyncio.create_task(
            self._wait_result(run_id, task)
        )

    async def _handle_cancel(self, request: ChatRequest):

        run_id = request["run_id"]

        logger.info(f"Cancelling run {run_id}")

        if self.run_manager.cancel(run_id):

            await self.emitter.cancelled(run_id)

    async def _wait_result(
        self,
        run_id: str,
        task: asyncio.Task,
    ):

        try:

            result = await task

            await self.emitter.finished(
                run_id,
                result.conversation_id,
                result.response,
            )

        except asyncio.CancelledError:

            logger.info(f"Run {run_id} cancelled")

        except Exception as e:

            logger.exception(e)

            await self.emitter.error(
                run_id,
                str(e),
            )

        finally:

            self.run_manager.remove(run_id)
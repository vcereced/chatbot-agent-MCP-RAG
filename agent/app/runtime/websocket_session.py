import asyncio
import uuid
from shared.agent.chat import ChatRequest
from fastapi import WebSocket, WebSocketDisconnect
from app.runtime.run_manager import RunManager
from app.runtime.emmiter import WebSocketEmitter
from app.services.chat_service import ChatService
from shared.logging.logger import (
    configure_logging,
    run_id_context,
    session_id_context,
)

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
        self.session_id = str(uuid.uuid4())

    async def run(self):
        session_token = session_id_context.set(self.session_id)

        try:
            logger.info("WebSocket session started")

            while True:
                request = await self.websocket.receive_json()

                if request["type"] == "message":
                    await self._handle_message(request)
                elif request["type"] == "cancel":
                    await self._handle_cancel(request)

        except WebSocketDisconnect as e:
            logger.info("WebSocket disconnected: %s", e.code)

        finally:
            self.run_manager.cancel_all()
            session_id_context.reset(session_token)

    async def _handle_message(self, request: ChatRequest):
        run_id = str(uuid.uuid4())
        token = run_id_context.set(run_id)
        try:
            logger.info("Run received")

            task = asyncio.create_task(
                self._run_chat(request, run_id)
            )
            self.run_manager.add(run_id, task)
        finally:
            # create_task copies the current context; restore the WebSocket
            # task so later messages do not inherit this run_id.
            run_id_context.reset(token)

    async def _run_chat(self, request: ChatRequest, run_id: str):

        try:
            logger.info("Run started")

            await self.emitter.started(
                run_id,
                "started",
                request.get("conversation_id"),
            )

            result = await self.chat_service.chat(
                conversation_id=request.get("conversation_id"),
                message=request["message"],
                emitter=self.emitter,
                run_id=run_id,
            )

            await self.emitter.finished(
                run_id,
                result.conversation_id,
                result.response,
            )

            logger.info("Run completed")

        except asyncio.CancelledError:
            logger.info("Run cancelled")
            raise

        except Exception:
            logger.exception("Run failed")

            await self.emitter.error(
                run_id,
                "Internal error",
            )

        finally:
            self.run_manager.remove(run_id)

    async def _handle_cancel(self, request: ChatRequest):
        run_id = request["run_id"]
        token = run_id_context.set(run_id)
        try:
            logger.info("Cancelling run %s", run_id)

            if self.run_manager.cancel(run_id):
                await self.emitter.cancelled(run_id)
        finally:
            run_id_context.reset(token)
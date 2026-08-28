from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from shared.agent.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService
from shared.logging.logger import configure_logging
from app.runtime.run_manager import RunManager
from app.runtime.websocket_session import WebSocketSession
import asyncio
import uuid

logger = configure_logging(__name__)

router = APIRouter()

service = ChatService()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    print(">>> WEBSOCKET ENDPOINT REGISTRADO <<<")
    await websocket.accept()

    session = WebSocketSession(
        websocket,
        service,
    )

    await session.run()

print(">>> chat.py importado <<<")
logger.info("router registrado")
logger.info(router.routes)
print(router.routes)
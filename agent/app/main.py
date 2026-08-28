from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi import WebSocket

from app.api.chat import router as chat_router
from shared.logging.logger import configure_logging

logger = configure_logging(__name__)


app = FastAPI()

logger.info(chat_router)
logger.info("---------------")
logger.info(chat_router.routes)
logger.info(type(chat_router))

# Incluir el router donde está el websocket /ws
app.include_router(chat_router)

logger.info("=== RUTAS DE LA APP ===")

for route in app.router.routes:
    logger.info(f"{type(route).__name__}: {getattr(route, 'path', '-')}")


@app.get("/health", status_code=200)
@app.get("/")
def root():
    return {"status": "ok"}

@app.websocket("/test")
async def test(websocket: WebSocket):
    await websocket.accept()
    await websocket.send_text("ok")
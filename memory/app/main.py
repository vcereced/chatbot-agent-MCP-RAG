from fastapi import FastAPI
from app.api.memory import router as memory_router

from shared.logging.logger import configure_logging

logger = configure_logging(__name__)

app = FastAPI()
app.include_router(memory_router)



@app.get("/health", status_code=200)
@app.get("/", status_code=200)
def root():

    return {
        "status": "ok"
    }

logger.info("Memory service started and ready to accept requests.")
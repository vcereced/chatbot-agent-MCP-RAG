from fastapi import FastAPI
from app.api.generate import router
from shared.logging.logger import configure_logging


logger = configure_logging(__name__)

app = FastAPI()
app.include_router(router)

@app.get("/health", status_code=200)
@app.get("/")
def root():
    logger.info("Received root request.")

    return {
        "status": "ok"
    }
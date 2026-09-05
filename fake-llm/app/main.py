from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.config import config

app = FastAPI(title=config.APP_NAME)
app.include_router(chat_router)


@app.get("/health", status_code=200)
@app.get("/", status_code=200)
def root():
    return {"status": "ok"}

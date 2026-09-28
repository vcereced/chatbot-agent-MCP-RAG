from fastapi import FastAPI, Request
from app.api.chat import router as chat_router
from app.config import config
from shared.logging.logger import run_id_context

app = FastAPI(title=config.APP_NAME)
@app.middleware("http")
async def logging_context(request: Request, call_next):

    run_id = request.headers.get("X-Run-ID")

    token = run_id_context.set(run_id)

    try:
        response = await call_next(request)
        return response

    finally:
        run_id_context.reset(token)

app.include_router(chat_router)


@app.get("/health", status_code=200)
@app.get("/", status_code=200)
def root():
    return {"status": "ok"}

from fastapi import FastAPI
from app.api.generate import router
from shared.logging.logger import configure_logging, RunIDMiddleware

logger = configure_logging(__name__)

app = FastAPI()
app.add_middleware(RunIDMiddleware)


app.include_router(router)

@app.get("/health", status_code=200)
@app.get("/")
def root():
    return {
        "status": "ok"
    }
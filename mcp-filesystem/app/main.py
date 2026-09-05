import uvicorn
from app.api.filesystem import server
from app.config import config
from shared.logging.logger import configure_logging
from mcp.server.transport_security import TransportSecuritySettings
from starlette.routing import Route
from starlette.responses import JSONResponse

logger = configure_logging(__name__)

async def health(request):
    return JSONResponse({"status": "ok"})

if __name__ == "__main__":

    security_settings = TransportSecuritySettings(
        allowed_hosts=[
            "mcp-filesystem:8000",
            "localhost:8000",
        ],
    )

    app = server.streamable_http_app(
        transport_security=security_settings,
    )

    app.routes.append(
        Route("/health", health, methods=["GET"])
    )

logger.info("mcpfilesystem service started and ready to accept requests.")
uvicorn.run(
    app,
    host=config.HOST,
    port=config.PORT,
)
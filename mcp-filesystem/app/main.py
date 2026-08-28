import uvicorn
from app.api.filesystem import server
from app.config import config
from shared.logging.logger import configure_logging
from mcp.server.transport_security import TransportSecuritySettings

logger = configure_logging(__name__)

if __name__ == "__main__":

    security_settings = TransportSecuritySettings(
        allowed_hosts=[
            "mcp-filesystem:8000",
        ],
    )

    app = server.streamable_http_app(
        transport_security=security_settings,
    )

logger.info("mcpfilesystem service started and ready to accept requests.")
uvicorn.run(
    app,
    host=config.HOST,
    port=config.PORT,
)
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.execute import router as execute_router
from app.config import settings
from app.registry.tool_registry import ToolRegistry
from app.mcp.mcp_manager import MCPManager
from app.manager.tool_manager import ToolManager
from app.service.tool_service import ToolService
from app.tools.calculator import CalculatorTool
from app.tools.datetime import DateTimeTool
from shared.logging.logger import configure_logging


logger = configure_logging(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):

    logger.info("Starting tools-executor service...")

    # Local tools
    registry = ToolRegistry()
    registry.register(CalculatorTool())
    registry.register(DateTimeTool())

    # MCP servers
    mcp_manager = MCPManager(settings.mcp_servers)

    # Conectar a todos los MCP y descubrir sus tools
    await mcp_manager.connect_all()

    # Unificar local tools + MCP tools
    tool_manager = ToolManager(
        registry=registry,
        mcp_manager=mcp_manager,
    )

    # Servicio que utilizarán los endpoints
    app.state.tool_service = ToolService(
        tool_manager=tool_manager,
    )

    logger.info("Tools-executor ready")

    yield

    logger.info("Shutting down tools-executor...")

    await mcp_manager.close_all()

    logger.info("Tools-executor stopped")


app = FastAPI(lifespan=lifespan)

app.include_router(execute_router)


@app.get("/health", status_code=200)
@app.get("/", status_code=200)
def health_check():
    return {
        "status": "ok",
        "service": "tools-executor",
    }
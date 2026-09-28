from fastapi import APIRouter, Request

from shared.tools.execute import ExecuteToolRequest, ExecuteToolResponse
from shared.tools.list_tools import ListToolsResponse
from shared.logging.logger import configure_logging


logger = configure_logging(__name__)

router = APIRouter()


@router.post("/execute", response_model=ExecuteToolResponse)
async def execute(
    request: Request,
    body: ExecuteToolRequest,
) -> ExecuteToolResponse:

    service = request.app.state.tool_service

    logger.info("Tool request received name=%s", body.tool_call.name)

    tool_result = await service.execute(
        body.tool_call
    )

    logger.info(
        "Tool request completed name=%s success=%s duration_ms=%s",
        tool_result.tool_name,
        tool_result.success,
        tool_result.execution_time_ms,
    )

    return ExecuteToolResponse(
        tool_result=tool_result
    )


@router.get("/tools", response_model=ListToolsResponse)
def list_tools(
    request: Request,
) -> ListToolsResponse:

    service = request.app.state.tool_service

    tools = service.list_tools()

    logger.info("Tool definitions listed count=%d", len(tools))

    return ListToolsResponse(
        tools=tools
    )
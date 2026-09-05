import json

import pytest
import websockets


AGENT_WS_URL = "ws://agent:8000/ws"


@pytest.mark.asyncio
async def test_to_agent_service():
    async with websockets.connect(AGENT_WS_URL) as websocket:

        message = {
            "type": "message",
            "conversation_id": None,
            "message": "test mensaje",
        }

        await websocket.send(json.dumps(message))

        while True:
            response = await websocket.recv()
            data = json.loads(response)

            if data["type"] == "finished":
                assert data["message"] == "test mensaje ok"
                print("TEST MENSAJE OK !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                break


@pytest.mark.asyncio
async def test_agent_executes_calculator_tool():
    async with websockets.connect(AGENT_WS_URL) as websocket:

        message = {
            "type": "message",
            "conversation_id": None,
            "message": "2+2",
        }

        await websocket.send(json.dumps(message))

        tool_execution_started = False

        while True:
            response = await websocket.recv()
            data = json.loads(response)

            if (
                data["type"] == "status"
                and data["message"] == "ejecutando herramienta del agente"
            ):
                tool_execution_started = True

            if data["type"] == "finished":
                assert tool_execution_started is True
                assert data["message"] == "4"
                break

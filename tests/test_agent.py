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

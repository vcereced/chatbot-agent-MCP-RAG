from fastapi import WebSocket


class WebSocketEmitter:

    def __init__(self, websocket: WebSocket):
        self._websocket = websocket

    async def started(self, run_id: str, message: str, conversation_id: str | None) -> None:

        await self._websocket.send_json({
            "type": "started",
            "run_id": run_id,
            "conversation_id": conversation_id,
            "message": message,

        })

    async def status(self, run_id: str, message: str) -> None:

        await self._websocket.send_json({
            "type": "status",
            "run_id": run_id,
            "message": message,
        })

    async def finished(self, run_id: str, conversation_id: str, message: str) -> None:

        await self._websocket.send_json({
            "type": "finished",
            "run_id": run_id,
            "conversation_id": conversation_id,
            "message": message,
        })

    async def cancelled(self, run_id: str) -> None:

        await self._websocket.send_json({
            "type": "cancelled",
            "run_id": run_id,
        })

    async def error(self, run_id: str, message: str) -> None:

        await self._websocket.send_json({
            "type": "error",
            "run_id": run_id,
            "message": message,
        })
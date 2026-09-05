from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

router = APIRouter(tags=["fake-llm"])


class ChatMessage(BaseModel):
    role: str
    content: str | None = None
    name: str | None = None


class ChatRequest(BaseModel):
    model: str = "fake-llm"
    messages: list[ChatMessage] = Field(default_factory=list)
    stream: bool = False
    tools: list[dict[str, Any]] | None = None


@router.post("/api/chat")
async def chat(payload: ChatRequest):
    last_user_message = payload.messages[-1]

    if last_user_message.content == "test mensaje":
        answer = {
            "model": payload.model,
            "created_at": "2026-09-03T17:47:15.0179614Z",
            "message": {
                "role": "assistant",
                "content": "test mensaje ok" #prueba para que falle aposta borrar EERRRRRR
            },
            "done": True,
            "done_reason": "stop",
            "total_duration": 169900138544,
            "load_duration": 14713452843,
            "prompt_eval_count": 227,
            "prompt_eval_duration": 146822765000,
            "eval_count": 11,
            "eval_duration": 8341436000
        }
    elif last_user_message.content in ("test tool", "2+2"):
        answer = {'model': 'qwen2.5:3b', 'created_at': '2026-09-03T18:01:52.276409928Z', 'message': {'role': 'assistant', 'content': '', 'tool_calls': [{'id': 'call_40lyef3s', 'function': {'index': 0, 'name': 'calculator', 'arguments': {'expression': '2 + 2'}}}]}, 'done': True, 'done_reason': 'stop', 'total_duration': 17953465405, 'load_duration': 1790606, 'prompt_eval_count': 230, 'prompt_eval_duration': 6555276000, 'eval_count': 15, 'eval_duration': 11374974000}
    elif last_user_message.role == "tool" and last_user_message.content == "4":
        answer = {'model': payload.model, 'created_at': '2026-09-03T18:10:45.563194995Z', 'message': {'role': 'assistant', 'content': '4'}, 'done': True, 'done_reason': 'stop'}
    else:
        answer = {'model': 'qwen2.5:3b', 'created_at': '2026-09-03T18:10:45.563194995Z', 'message': {'role': 'assistant', 'content': 'test tool ok'}, 'done': True, 'done_reason': 'stop', 'total_duration': 61870277754, 'load_duration': 4976463, 'prompt_eval_count': 67, 'prompt_eval_duration': 28250053000, 'eval_count': 43, 'eval_duration': 33600504999}
    return answer

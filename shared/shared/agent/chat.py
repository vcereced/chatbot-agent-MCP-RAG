from pydantic import BaseModel
from typing import Literal

class ChatRequest(BaseModel):

    type: Literal[
            "message",
            "cancel",
        ]
        
    conversation_id: str | None = None

    message: str

class ChatResponse(BaseModel):

    conversation_id: str

    message: str# ??CHAT RESULT
from pydantic import BaseModel

class ChatResult(BaseModel):

    conversation_id: str

    response: str
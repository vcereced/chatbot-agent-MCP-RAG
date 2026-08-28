from pydantic import BaseModel
from shared.domain.message import Message

class Conversation(BaseModel):

    id: str

    messages: list[Message]
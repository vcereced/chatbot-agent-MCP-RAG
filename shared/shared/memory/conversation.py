from pydantic import BaseModel
from shared.domain.conversation import Conversation

class GetOrCreateConversationRequest(BaseModel):

    conversation_id: str | None = None

class GetOrCreateConversationResponse(BaseModel):

    conversation: Conversation

class SaveConversationRequest(BaseModel):

    conversation: Conversation

class SaveConversationResponse(BaseModel):

    success: bool
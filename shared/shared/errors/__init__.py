

class ConversationNotFound(Exception):

    def __init__(self, conversation_id: str):

        super().__init__(
            f"Conversation '{conversation_id}' not found."
        )

        self.conversation_id = conversation_id
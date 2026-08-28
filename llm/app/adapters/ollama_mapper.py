from shared.domain.conversation import Conversation
from shared.domain.message import Message
from shared.domain.toolcall import ToolCall
from shared.domain.tooldefinition import ToolDefinition, ParameterDefinition, PropertyDefinition
from shared.domain.generate_result import GenerateResult


class OllamaMapper:

    @staticmethod
    def to_messages(messages: list[Message]) -> list[dict]:

        result = []

        for message in messages:

            if message.role == "assistant" and message.tool_call is not None:

                result.append({
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "function": {
                                "name": message.tool_call.name,
                                "arguments": message.tool_call.arguments,
                            }
                        }
                    ],
                })

            elif message.role == "tool":

                result.append({
                    "role": "tool",
                    "content": message.content,
                    "name": message.tool_name,
                })

            else:

                result.append({
                    "role": message.role,
                    "content": message.content,
                })

        return result

    @staticmethod
    def to_tools(tools: list[ToolDefinition] | None) -> list[dict]:

        if tools is None:
            return []
        
        ollama_tools = []

        for tool in tools:

            properties = {}

            for name, definition in tool.input_schema.properties.items():

                properties[name] = {
                    "type": definition.type,
                    "description": definition.description,
                }

            ollama_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "input_schema": {
                        "type": tool.input_schema.type,
                        "properties": properties,
                        "required": tool.input_schema.required,
                    },
                },
            })

        return ollama_tools

    @staticmethod
    def to_generate_result(response: dict) -> GenerateResult:

        message = response["message"]

        if message.get("tool_calls"):

            function = message["tool_calls"][0]["function"]

            return GenerateResult(
                tool_call=ToolCall(
                    name=function["name"],
                    arguments=function["arguments"],
                )
            )

        return GenerateResult(
            text=message["content"]
        )
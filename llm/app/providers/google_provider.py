import base64

from google import genai
from google.genai import types

from app.config import config
from shared.domain.generate_result import GenerateResult
from shared.domain.message import Message
from shared.domain.toolcall import ToolCall
from shared.domain.tooldefinition import ToolDefinition
from app.providers.base_provider import BaseProvider


class GoogleProvider(BaseProvider):

    def __init__(self) -> None:
        if not config.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY es obligatoria para usar Google")

        self.model = config.GOOGLE_MODEL
        self.client = genai.Client(api_key=config.GOOGLE_API_KEY)

    async def generate(
        self,
        messages: list[Message],
        tools: list[ToolDefinition] | None,
    ) -> GenerateResult:
        response = await self.client.aio.models.generate_content(
            model=self.model,
            contents=self._to_contents(messages),
            config=types.GenerateContentConfig(
                system_instruction=config.SYSTEM_PROMPT,
                tools=self._to_tools(tools),
            ),
        )

        for part in response.candidates[0].content.parts:
            if part.function_call is not None:
                thought_signature = getattr(part, "thought_signature", None)
                if isinstance(thought_signature, bytes):
                    thought_signature = base64.b64encode(
                        thought_signature
                    ).decode("ascii")

                return GenerateResult(
                    tool_call=ToolCall(
                        name=part.function_call.name,
                        arguments=dict(part.function_call.args or {}),
                        thought_signature=thought_signature,
                    )
                )

        return GenerateResult(text=response.text or "")

    @staticmethod
    def _to_contents(messages: list[Message]) -> list[types.Content]:
        contents = []

        for message in messages:
            if message.role == "system":
                continue

            if message.role == "tool":
                contents.append(
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_function_response(
                                name=message.tool_name or "tool",
                                response={"result": message.content or ""},
                            )
                        ],
                    )
                )
                continue

            role = "model" if message.role == "assistant" else "user"
            parts = [types.Part.from_text(text=message.content or "")]

            if message.tool_call is not None:
                function_call = types.FunctionCall(
                    name=message.tool_call.name,
                    args=message.tool_call.arguments,
                )
                part_kwargs = {"function_call": function_call}

                if message.tool_call.thought_signature:
                    part_kwargs["thought_signature"] = base64.b64decode(
                        message.tool_call.thought_signature
                    )

                parts = [types.Part(**part_kwargs)]

            contents.append(types.Content(role=role, parts=parts))

        return contents

    @staticmethod
    def _to_tools(
        tools: list[ToolDefinition] | None,
    ) -> list[types.Tool] | None:
        if not tools:
            return None

        return [
            types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(
                        name=tool.name,
                        description=tool.description,
                        parameters_json_schema=tool.input_schema.model_dump(
                            by_alias=True,
                            exclude_none=True,
                        ),
                    )
                ]
            )
            for tool in tools
        ]

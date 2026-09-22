from abc import ABC, abstractmethod
from shared.domain.generate_result import GenerateResult
from shared.domain.message import Message
from shared.domain.tooldefinition import ToolDefinition


class BaseProvider(ABC):

    @abstractmethod
    async def generate(
        self,
        messages: list[Message],
        tools: list[ToolDefinition] | None,
    ) -> GenerateResult:
        raise NotImplementedError
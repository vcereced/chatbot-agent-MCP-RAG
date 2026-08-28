from abc import ABC, abstractmethod
from shared.domain.tooldefinition import ToolDefinition


class BaseTool(ABC):
    
    @abstractmethod
    def get_definition(self) -> ToolDefinition:
        """Descripción y esquema de la herramienta."""
        pass

    @abstractmethod
    async def execute(self, arguments: dict[str, str]) -> object:
        """Ejecuta la herramienta recibiendo los argumentos."""
        pass
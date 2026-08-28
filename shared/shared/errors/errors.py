class MemoryStorageError(Exception):
    """Se lanza cuando ocurre un fallo al leer o escribir en el almacenamiento de memoria."""
    def __init__(self, message: str = "Error en el almacenamiento de memoria"):
        self.message = message
        super().__init__(self.message)

class LLMProviderError(Exception):
    """Excepción base para fallos en el proveedor de LLM (Ollama, OpenAI, etc.)."""
    def __init__(self, message: str = "Error en el proveedor de LLM"):
        self.message = message
        super().__init__(self.message)


class LLMConnectionError(LLMProviderError):
    """Ocurre cuando no se puede conectar con el servicio del LLM."""
    pass


class LLMTimeoutError(LLMProviderError):
    """Ocurre cuando el servicio del LLM no responde dentro del tiempo límite."""
    pass

class MCPConnectionError(Exception):
    """Error al conectar o comunicarse con un servidor MCP."""

    pass
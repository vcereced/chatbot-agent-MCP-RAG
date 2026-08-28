from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # Configuración del Proveedor (Ollama)
    OLLAMA_MODEL: str 
    OLLAMA_ENDPOINT: str = "/api/chat"
    OLLAMA_BASE_URL: str  #si lo corremos en local y no en docker
    TIMEOUT: float = 300.0

    # Prompts de Sistema
    SYSTEM_PROMPT: str = """
                You are a helpful assistant.

                Always answer in Spanish.

                You have access to tools.

                When a tool is needed, you MUST call the tool.
                Do not describe the tool call.
                Do not print JSON.
                Do not explain that you are calling a tool.
                Return a tool call instead of text.
                """.strip()



# Inyección por caché para no releer el disco/entorno en cada llamada
@lru_cache
def get_settings() -> Settings:
    return Settings()

config = get_settings()

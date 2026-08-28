from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Agent Service"
    DEBUG: bool = False

    # URLs de los otros microservicios (Nombres de servicio en Docker Compose)
    LLM_URL: str 
    TOOLS_URL: str 
    MEMORY_URL: str  
    REQUEST_TIMEOUT: str  

@lru_cache
def get_settings() -> Settings:
    return Settings()

config = get_settings()


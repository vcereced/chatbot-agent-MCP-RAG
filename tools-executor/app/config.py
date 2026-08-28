from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel
import os


class MCPConfig(BaseModel):
    name: str
    url: str


class Settings(BaseSettings):
    # --- Configuración del Microservicio ---
    log_level: str = Field(default="INFO", description="Nivel de logging (DEBUG, INFO, ERROR)")
    
    # --- Timeouts y Límites ---
    tool_timeout_seconds: float = Field(
        default=30.0, 
        description="Tiempo máximo de ejecución para una herramienta"
    )

    mcp_servers: list[MCPConfig] = [
        MCPConfig(
            name=os.getenv("MCP_NAME_1", ""),
            url=os.getenv("MCP_URL_1", ""),
        ),
        # MCPConfig(
        #     name="github",
        #     url="http://mcp-github:8000/mcp",
        # ),
    ]


settings = Settings()

# Usamos lru_cache para que la lectura e instanciación de las variables 
# ocurra UNA sola vez en memoria (Patrón Singleton en producción)
@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Exportamos la instancia para uso directo
settings = get_settings()
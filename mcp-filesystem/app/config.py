import os


class Config:
    HOST: str = os.getenv("MCP_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("MCP_PORT", "8000"))
    ALLOWED_DIRECTORY: str = os.getenv(
        "MCP_ALLOWED_DIRECTORY",
        "/projects",
    )


config = Config()
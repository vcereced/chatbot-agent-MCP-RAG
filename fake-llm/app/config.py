from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "fake-llm"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


config = Settings()

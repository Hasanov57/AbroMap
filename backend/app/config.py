from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./abromap.db"
    frontend_origin: str = "http://localhost:3000"
    admin_token: str | None = None
    openai_api_key: str | None = None
    openai_model: str = "gpt-4.1-mini"

    @field_validator("database_url", mode="before")
    @classmethod
    def use_psycopg(cls, value: str) -> str:
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+psycopg://", 1)
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

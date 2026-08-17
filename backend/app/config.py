from functools import lru_cache
from pathlib import Path

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "CampusOS API"
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    database_url: str = "postgresql+psycopg://campusos:change-me@localhost:5432/campusos"
    jwt_secret_key: str = Field(min_length=32, description="Required. Set this in backend/.env; never use a development secret in production.")
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = Field(default=30, ge=1, le=1440)
    jwt_refresh_token_expire_days: int = Field(default=7, ge=1, le=90)
    frontend_url: str = "http://localhost:3000"
    upload_dir: Path = Path("./uploads")
<<<<<<< HEAD
    max_image_size: int = 2 * 1024 * 1024
    max_video_size: int = 5 * 1024 * 1024
=======
    max_image_size: int = 5 * 1024 * 1024
    max_video_size: int = 20 * 1024 * 1024
>>>>>>> 1b8878ef404f483e7609ab1c87da6c2e8c648546
    primary_ai_provider: str = "gemini"
    fallback_ai_provider: str = "openai"
    secondary_fallback_ai_provider: str = "deepseek"
    openai_api_key: str | None = None
    gemini_api_key: str | None = None
    deepseek_api_key: str | None = None

    @field_validator("frontend_url")
    @classmethod
    def valid_frontend_url(cls, value: str) -> str:
        AnyHttpUrl(value)
        return value.rstrip("/")


@lru_cache
def get_settings() -> Settings:
    return Settings()

"""
config.py - Single Source of Truth for Application Configuration
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    app_name: str = "SecureAPI"
    app_version: str = "1.0.0"
    environment: str = "development"

    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30

    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = False
    
    log_level: str = "INFO"
    log_file: str = "logs/app.log"
    
    groq_api_key: str
    groq_model: str = "llama-3.3-70b-versatile"

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
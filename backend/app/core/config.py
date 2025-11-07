"""Application configuration"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # API Configuration
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True

    # CORS Configuration
    cors_origins: List[str] = ["http://localhost:5173", "http://localhost:3000"]

    # Extraction Configuration
    extraction_timeout: int = 10
    max_concurrent_requests: int = 10
    max_retries: int = 3

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

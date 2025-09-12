import os
from functools import lru_cache
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://pixel_user:pixel_secure_2024@localhost:5433/pixel_ai",
    )

    # Individual Database Components (for Database Manager)
    DATABASE_HOST: str = os.getenv("DATABASE_HOST", "localhost")
    DATABASE_PORT: int = int(os.getenv("DATABASE_PORT", "5433"))
    DATABASE_NAME: str = os.getenv("DATABASE_NAME", "pixel_ai")
    DATABASE_USER: str = os.getenv("DATABASE_USER", "pixel_user")
    DATABASE_PASSWORD: str = os.getenv("DATABASE_PASSWORD", "pixel_secure_2024")

    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    redis_host: str = os.getenv("REDIS_HOST", "localhost")
    redis_port: int = int(os.getenv("REDIS_PORT", "6379"))

    # AI Services
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")

    # ChromaDB
    chromadb_host: str = os.getenv("CHROMADB_HOST", "localhost")
    chromadb_port: int = int(os.getenv("CHROMADB_PORT", "8003"))

    # Security
    secret_key: str = os.getenv("SECRET_KEY", "pixel-ai-secret-key-2024")
    access_token_expire_minutes: int = 30

    # Social Media APIs
    twitter_bearer_token: Optional[str] = os.getenv("TWITTER_BEARER_TOKEN")
    instagram_access_token: Optional[str] = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    linkedin_client_id: Optional[str] = os.getenv("LINKEDIN_CLIENT_ID")
    linkedin_client_secret: Optional[str] = os.getenv("LINKEDIN_CLIENT_SECRET")

    # Social Authentication
    GOOGLE_CLIENT_ID: Optional[str] = os.getenv("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET: Optional[str] = os.getenv("GOOGLE_CLIENT_SECRET")
    GITHUB_CLIENT_ID: Optional[str] = os.getenv("GITHUB_CLIENT_ID")
    GITHUB_CLIENT_SECRET: Optional[str] = os.getenv("GITHUB_CLIENT_SECRET")
    LINKEDIN_CLIENT_ID: Optional[str] = os.getenv("LINKEDIN_CLIENT_ID")
    LINKEDIN_CLIENT_SECRET: Optional[str] = os.getenv("LINKEDIN_CLIENT_SECRET")

    # Base URL for OAuth callbacks
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")

    # MFA Encryption
    MFA_ENCRYPTION_KEY: str = os.getenv(
        "MFA_ENCRYPTION_KEY", "pixel-mfa-encryption-key-2024-secure"
    )

    # Application
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = environment == "development"

    # File storage
    generated_bots_dir: str = "/app/generated-bots"
    templates_dir: str = "/app/templates"

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Create global settings instance
settings = get_settings()


settings = Settings()

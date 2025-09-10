import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://pixel_user:pixel_secure_2024@localhost:5432/pixel_ai")
    
    # Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # AI Services
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # ChromaDB
    chromadb_host: str = os.getenv("CHROMADB_HOST", "localhost")
    chromadb_port: int = int(os.getenv("CHROMADB_PORT", "8001"))
    
    # Security
    secret_key: str = os.getenv("SECRET_KEY", "pixel-ai-secret-key-2024")
    access_token_expire_minutes: int = 30
    
    # Social Media APIs
    twitter_bearer_token: Optional[str] = os.getenv("TWITTER_BEARER_TOKEN")
    instagram_access_token: Optional[str] = os.getenv("INSTAGRAM_ACCESS_TOKEN")
    linkedin_client_id: Optional[str] = os.getenv("LINKEDIN_CLIENT_ID")
    linkedin_client_secret: Optional[str] = os.getenv("LINKEDIN_CLIENT_SECRET")
    
    # Application
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = environment == "development"
    
    # File storage
    generated_bots_dir: str = "/app/generated-bots"
    templates_dir: str = "/app/templates"
    
    class Config:
        env_file = ".env"

settings = Settings()

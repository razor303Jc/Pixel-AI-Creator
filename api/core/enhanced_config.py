"""
Enhanced Configuration Settings for Database Management
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, validator
from functools import lru_cache


class DatabaseSettings(BaseSettings):
    """Database configuration settings"""

    # Core database settings
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", "postgresql+asyncpg://user:password@localhost:5432/pixel_ai_db"
    )

    # Connection pool settings
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "5"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    DB_POOL_TIMEOUT: int = int(os.getenv("DB_POOL_TIMEOUT", "30"))
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))
    DB_POOL_PRE_PING: bool = os.getenv("DB_POOL_PRE_PING", "true").lower() == "true"

    # Connection monitoring
    DB_HEALTH_CHECK_INTERVAL: int = int(os.getenv("DB_HEALTH_CHECK_INTERVAL", "30"))
    DB_CONNECTION_TIMEOUT: int = int(os.getenv("DB_CONNECTION_TIMEOUT", "10"))
    DB_QUERY_TIMEOUT: int = int(os.getenv("DB_QUERY_TIMEOUT", "60"))

    # Performance monitoring
    DB_SLOW_QUERY_THRESHOLD: float = float(os.getenv("DB_SLOW_QUERY_THRESHOLD", "1.0"))
    DB_METRICS_RETENTION_HOURS: int = int(
        os.getenv("DB_METRICS_RETENTION_HOURS", "168")
    )  # 7 days
    DB_ENABLE_QUERY_LOGGING: bool = (
        os.getenv("DB_ENABLE_QUERY_LOGGING", "false").lower() == "true"
    )

    # Backup settings
    BACKUP_DIRECTORY: str = os.getenv("BACKUP_DIRECTORY", "/app/backups")
    BACKUP_ENCRYPTION_KEY: Optional[str] = os.getenv("BACKUP_ENCRYPTION_KEY")
    BACKUP_RETENTION_DAYS: int = int(os.getenv("BACKUP_RETENTION_DAYS", "30"))
    BACKUP_COMPRESSION_LEVEL: int = int(os.getenv("BACKUP_COMPRESSION_LEVEL", "6"))
    BACKUP_MAX_PARALLEL: int = int(os.getenv("BACKUP_MAX_PARALLEL", "2"))

    # Security settings
    DB_AUDIT_ENABLED: bool = os.getenv("DB_AUDIT_ENABLED", "true").lower() == "true"
    DB_ENCRYPTION_ENABLED: bool = (
        os.getenv("DB_ENCRYPTION_ENABLED", "true").lower() == "true"
    )
    DB_AUDIT_RETENTION_DAYS: int = int(os.getenv("DB_AUDIT_RETENTION_DAYS", "90"))
    DB_ENABLE_DATA_MASKING: bool = (
        os.getenv("DB_ENABLE_DATA_MASKING", "true").lower() == "true"
    )

    # Alert thresholds
    ALERT_CONNECTION_THRESHOLD: float = float(
        os.getenv("ALERT_CONNECTION_THRESHOLD", "0.8")
    )  # 80%
    ALERT_RESPONSE_TIME_THRESHOLD: float = float(
        os.getenv("ALERT_RESPONSE_TIME_THRESHOLD", "2000")
    )  # 2s
    ALERT_ERROR_RATE_THRESHOLD: float = float(
        os.getenv("ALERT_ERROR_RATE_THRESHOLD", "0.05")
    )  # 5%
    ALERT_DISK_USAGE_THRESHOLD: float = float(
        os.getenv("ALERT_DISK_USAGE_THRESHOLD", "0.9")
    )  # 90%

    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        if not v or not v.startswith(("postgresql://", "postgresql+asyncpg://")):
            raise ValueError("DATABASE_URL must be a valid PostgreSQL URL")
        return v

    @validator("BACKUP_DIRECTORY")
    def validate_backup_directory(cls, v):
        if not os.path.isabs(v):
            raise ValueError("BACKUP_DIRECTORY must be an absolute path")
        return v

    class Config:
        env_file = ".env"
        case_sensitive = True


class ApplicationSettings(BaseSettings):
    """Main application settings"""

    # App configuration
    APP_NAME: str = "Pixel AI Creator"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ]

    # Redis configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_CACHE_TTL: int = int(os.getenv("REDIS_CACHE_TTL", "300"))

    # File upload settings
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    UPLOAD_DIRECTORY: str = os.getenv("UPLOAD_DIRECTORY", "/app/uploads")

    # Email settings (for alerts)
    SMTP_SERVER: Optional[str] = os.getenv("SMTP_SERVER")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: Optional[str] = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD")
    ALERT_EMAIL_FROM: Optional[str] = os.getenv("ALERT_EMAIL_FROM")
    ALERT_EMAIL_TO: List[str] = (
        os.getenv("ALERT_EMAIL_TO", "").split(",")
        if os.getenv("ALERT_EMAIL_TO")
        else []
    )

    # Monitoring and logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"
    METRICS_PORT: int = int(os.getenv("METRICS_PORT", "9090"))

    # AI/ML settings
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    MAX_TOKENS_PER_REQUEST: int = int(os.getenv("MAX_TOKENS_PER_REQUEST", "4000"))
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")

    @validator("ALLOWED_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @validator("ALERT_EMAIL_TO", pre=True)
    def parse_alert_emails(cls, v):
        if isinstance(v, str):
            return [email.strip() for email in v.split(",") if email.strip()]
        return v if isinstance(v, list) else []

    class Config:
        env_file = ".env"
        case_sensitive = True


class Settings(ApplicationSettings, DatabaseSettings):
    """Combined settings class"""

    pass


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Create global settings instance
settings = get_settings()


# Environment-specific configurations
class DevelopmentConfig(Settings):
    """Development environment configuration"""

    DEBUG: bool = True
    DB_ENABLE_QUERY_LOGGING: bool = True
    BACKUP_RETENTION_DAYS: int = 7
    DB_METRICS_RETENTION_HOURS: int = 24


class ProductionConfig(Settings):
    """Production environment configuration"""

    DEBUG: bool = False
    DB_ENABLE_QUERY_LOGGING: bool = False
    BACKUP_RETENTION_DAYS: int = 90
    DB_METRICS_RETENTION_HOURS: int = 168  # 7 days

    @validator("SECRET_KEY")
    def validate_production_secret(cls, v):
        if v == "dev-secret-key-change-in-production":
            raise ValueError("SECRET_KEY must be changed in production")
        return v

    @validator("BACKUP_ENCRYPTION_KEY")
    def validate_backup_encryption(cls, v):
        if not v:
            raise ValueError("BACKUP_ENCRYPTION_KEY is required in production")
        return v


class TestingConfig(Settings):
    """Testing environment configuration"""

    DEBUG: bool = True
    DATABASE_URL: str = "postgresql+asyncpg://test:test@localhost:5432/test_db"
    DB_POOL_SIZE: int = 2
    BACKUP_RETENTION_DAYS: int = 1
    DB_AUDIT_ENABLED: bool = False


def get_config_by_env(env: str = None) -> Settings:
    """Get configuration based on environment"""
    env = env or os.getenv("ENVIRONMENT", "development").lower()

    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig,
    }

    config_class = config_map.get(env, DevelopmentConfig)
    return config_class()


# Database URL helpers
def get_sync_database_url() -> str:
    """Get synchronous database URL for migrations"""
    url = settings.DATABASE_URL
    if url.startswith("postgresql+asyncpg://"):
        return url.replace("postgresql+asyncpg://", "postgresql://")
    return url


def get_redis_config() -> dict:
    """Get Redis configuration dictionary"""
    return {
        "url": settings.REDIS_URL,
        "encoding": "utf-8",
        "decode_responses": True,
        "socket_connect_timeout": 5,
        "socket_timeout": 5,
        "retry_on_timeout": True,
        "health_check_interval": 30,
    }


# Logging configuration
def get_logging_config() -> dict:
    """Get logging configuration"""
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.LOG_LEVEL,
                "formatter": "default",
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "detailed",
                "filename": "logs/app.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
            },
        },
        "loggers": {
            "api": {
                "level": settings.LOG_LEVEL,
                "handlers": ["console", "file"],
                "propagate": False,
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "sqlalchemy": {
                "level": "WARNING",
                "handlers": ["console"],
                "propagate": False,
            },
        },
        "root": {
            "level": settings.LOG_LEVEL,
            "handlers": ["console"],
        },
    }

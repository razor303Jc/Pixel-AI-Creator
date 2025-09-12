"""
Logging Configuration
Centralized logging setup for the API
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """
    Set up logging configuration

    Args:
        level: Logging level (default: INFO)

    Returns:
        Configured logger
    """
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Configure logging format
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        logs_dir / "api.log", maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    # Configure root logger
    logger = logging.getLogger("api")
    logger.setLevel(level)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    return logging.getLogger(f"api.{name}")


# Initialize default logger
default_logger = setup_logging()

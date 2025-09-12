"""
Redis Caching Service for Pixel AI Creator.

Provides comprehensive caching strategies for frequent queries,
API responses, and database optimization.
"""

import json
import redis
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import pickle
from pydantic import BaseModel

from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class CacheConfig(BaseModel):
    """Cache configuration settings."""

    default_ttl: int = 3600  # 1 hour
    api_response_ttl: int = 300  # 5 minutes
    database_query_ttl: int = 1800  # 30 minutes
    analytics_ttl: int = 7200  # 2 hours
    conversation_ttl: int = 86400  # 24 hours
    user_session_ttl: int = 28800  # 8 hours


class CacheKeyBuilder:
    """Utility class for building consistent cache keys."""

    @staticmethod
    def user_profile(user_id: int) -> str:
        return f"user:profile:{user_id}"

    @staticmethod
    def chatbot_config(chatbot_id: int) -> str:
        return f"chatbot:config:{chatbot_id}"

    @staticmethod
    def conversation_history(conversation_id: int) -> str:
        return f"conversation:history:{conversation_id}"

    @staticmethod
    def analytics_summary(user_id: int, date: str) -> str:
        return f"analytics:summary:{user_id}:{date}"

    @staticmethod
    def api_response(endpoint: str, params: str) -> str:
        """Generate cache key for API responses."""
        param_hash = hashlib.md5(params.encode()).hexdigest()[:8]
        return f"api:response:{endpoint}:{param_hash}"

    @staticmethod
    def database_query(table: str, query_hash: str) -> str:
        return f"db:query:{table}:{query_hash}"

    @staticmethod
    def language_detection(text_hash: str) -> str:
        return f"language:detection:{text_hash}"

    @staticmethod
    def translation_cache(text_hash: str, source: str, target: str) -> str:
        return f"translation:{source}:{target}:{text_hash}"


class RedisCache:
    """Redis caching service with advanced features."""

    def __init__(self):
        self.config = CacheConfig()
        self.redis_client = None
        self.is_connected = False
        self._connect()

    def _connect(self):
        """Connect to Redis server."""
        try:
            # Parse redis_url to get connection details
            redis_url = settings.redis_url
            if redis_url.startswith("redis://"):
                # Extract host and port from redis_url
                url_parts = redis_url.replace("redis://", "").split(":")
                host = url_parts[0] if url_parts else "localhost"
                port = int(url_parts[1]) if len(url_parts) > 1 else 6379

                self.redis_client = redis.Redis(
                    host=host,
                    port=port,
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5,
                    retry_on_timeout=True,
                )
            else:
                # Fallback to simple redis connection
                self.redis_client = redis.from_url(
                    settings.redis_url,
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5,
                    retry_on_timeout=True,
                )

            # Test connection
            self.redis_client.ping()
            self.is_connected = True
            logger.info("Redis cache connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            self.is_connected = False

    def _ensure_connection(self):
        """Ensure Redis connection is active."""
        if not self.is_connected:
            self._connect()

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set cache value with optional TTL."""
        if not self.is_connected:
            return False

        try:
            # Serialize complex objects
            if isinstance(value, (dict, list, BaseModel)):
                if isinstance(value, BaseModel):
                    value = value.dict()
                value = json.dumps(value, default=str)

            ttl = ttl or self.config.default_ttl
            result = self.redis_client.setex(key, ttl, value)
            return bool(result)
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    def get(self, key: str) -> Optional[Any]:
        """Get cache value."""
        if not self.is_connected:
            return None

        try:
            value = self.redis_client.get(key)
            if value is None:
                return None

            # Try to deserialize JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None

    def delete(self, key: str) -> bool:
        """Delete cache key."""
        if not self.is_connected:
            return False

        try:
            result = self.redis_client.delete(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if cache key exists."""
        if not self.is_connected:
            return False

        try:
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Cache exists check error for key {key}: {e}")
            return False

    def get_ttl(self, key: str) -> int:
        """Get remaining TTL for cache key."""
        if not self.is_connected:
            return -1

        try:
            return self.redis_client.ttl(key)
        except Exception as e:
            logger.error(f"Cache TTL check error for key {key}: {e}")
            return -1

    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment cache value."""
        if not self.is_connected:
            return None

        try:
            return self.redis_client.incr(key, amount)
        except Exception as e:
            logger.error(f"Cache increment error for key {key}: {e}")
            return None

    def set_hash(
        self, key: str, field: str, value: Any, ttl: Optional[int] = None
    ) -> bool:
        """Set hash field value."""
        if not self.is_connected:
            return False

        try:
            if isinstance(value, (dict, list, BaseModel)):
                if isinstance(value, BaseModel):
                    value = value.dict()
                value = json.dumps(value, default=str)

            result = self.redis_client.hset(key, field, value)
            if ttl:
                self.redis_client.expire(key, ttl)
            return bool(result)
        except Exception as e:
            logger.error(f"Cache hash set error for key {key}, field {field}: {e}")
            return False

    def get_hash(self, key: str, field: str) -> Optional[Any]:
        """Get hash field value."""
        if not self.is_connected:
            return None

        try:
            value = self.redis_client.hget(key, field)
            if value is None:
                return None

            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
        except Exception as e:
            logger.error(f"Cache hash get error for key {key}, field {field}: {e}")
            return None

    def get_all_hash(self, key: str) -> Dict[str, Any]:
        """Get all hash fields and values."""
        if not self.is_connected:
            return {}

        try:
            hash_data = self.redis_client.hgetall(key)
            result = {}
            for field, value in hash_data.items():
                try:
                    result[field] = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    result[field] = value
            return result
        except Exception as e:
            logger.error(f"Cache hash getall error for key {key}: {e}")
            return {}

    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        if not self.is_connected:
            return 0

        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                return self.redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error for pattern {pattern}: {e}")
            return 0

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        if not self.is_connected:
            return {"connected": False}

        try:
            info = self.redis_client.info()
            return {
                "connected": True,
                "used_memory": info.get("used_memory_human", "0"),
                "total_keys": (
                    info.get("db0", {}).get("keys", 0) if "db0" in info else 0
                ),
                "hits": info.get("keyspace_hits", 0),
                "misses": info.get("keyspace_misses", 0),
                "hit_rate": (
                    info.get("keyspace_hits", 0)
                    / max(
                        info.get("keyspace_hits", 0) + info.get("keyspace_misses", 0), 1
                    )
                )
                * 100,
                "uptime_seconds": info.get("uptime_in_seconds", 0),
            }
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {"connected": False, "error": str(e)}


# Global cache instance
cache = RedisCache()


def cached(ttl: Optional[int] = None, key_prefix: str = ""):
    """Decorator for caching function results."""

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            func_name = f"{key_prefix}{func.__name__}" if key_prefix else func.__name__
            key_data = f"{args}{kwargs}"
            key_hash = hashlib.md5(key_data.encode()).hexdigest()[:8]
            cache_key = f"func:{func_name}:{key_hash}"

            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func_name}")
                return cached_result

            # Execute function and cache result
            logger.debug(f"Cache miss for {func_name}")
            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            func_name = f"{key_prefix}{func.__name__}" if key_prefix else func.__name__
            key_data = f"{args}{kwargs}"
            key_hash = hashlib.md5(key_data.encode()).hexdigest()[:8]
            cache_key = f"func:{func_name}:{key_hash}"

            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"Cache hit for {func_name}")
                return cached_result

            # Execute function and cache result
            logger.debug(f"Cache miss for {func_name}")
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result

        # Return appropriate wrapper based on function type
        import inspect

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator

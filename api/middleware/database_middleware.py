"""
Database Management Middleware
Provides middleware integration for database management features
"""

from typing import Dict, Any, Optional, List
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import time
import json
import logging
from datetime import datetime, timedelta
import asyncpg
import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import uuid

from core.database_manager import DatabaseConnectionManager
from services.database_monitor import DatabaseMonitor, AlertLevel, MetricType
from api.core.database import get_db
from api.core.config import settings

logger = logging.getLogger(__name__)


class DatabaseMiddleware(BaseHTTPMiddleware):
    """
    Middleware for database request monitoring and management
    """

    def __init__(self, app, db_manager: DatabaseConnectionManager):
        super().__init__(app)
        self.db_manager = db_manager
        self.monitor = DatabaseMonitor(db_manager)
        self.redis_client: Optional[redis.Redis] = None

    async def setup_redis(self):
        """Setup Redis connection for caching and session management"""
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL, encoding="utf-8", decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Redis connection established for database middleware")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            self.redis_client = None

    async def dispatch(self, request: Request, call_next):
        """Process database-related requests with monitoring"""
        start_time = time.time()
        request_id = str(uuid.uuid4())

        # Add request ID to headers
        request.state.request_id = request_id

        # Track database operations
        db_operations = []
        original_db = request.state.__dict__.get("db")

        try:
            # Monitor database health before processing
            if request.url.path.startswith("/api/database"):
                health = await self.monitor.check_health()
                if health["status"] == "critical":
                    raise HTTPException(
                        status_code=503, detail="Database service unavailable"
                    )

            # Process request
            response = await call_next(request)

            # Record metrics
            processing_time = (time.time() - start_time) * 1000
            await self._record_request_metrics(
                request, response, processing_time, db_operations
            )

            # Add performance headers
            response.headers["X-Response-Time"] = f"{processing_time:.2f}ms"
            response.headers["X-Request-ID"] = request_id

            return response

        except Exception as e:
            # Record error metrics
            processing_time = (time.time() - start_time) * 1000
            await self._record_error_metrics(request, str(e), processing_time)

            # Alert on critical errors
            if isinstance(e, asyncpg.PostgresError):
                await self.monitor.record_metric(
                    MetricType.ERROR_RATE,
                    1.0,
                    {"error_type": "database", "error": str(e)},
                )

            raise e

        finally:
            # Cleanup and final monitoring
            await self._cleanup_request(request_id)

    async def _record_request_metrics(
        self,
        request: Request,
        response: Response,
        processing_time: float,
        db_operations: List[Dict[str, Any]],
    ):
        """Record request metrics for monitoring"""
        try:
            # Basic request metrics
            await self.monitor.record_metric(
                MetricType.RESPONSE_TIME,
                processing_time,
                {
                    "endpoint": request.url.path,
                    "method": request.method,
                    "status_code": response.status_code,
                },
            )

            # Database operation metrics
            if db_operations:
                total_db_time = sum(op.get("duration", 0) for op in db_operations)
                await self.monitor.record_metric(
                    MetricType.QUERY_EXECUTION_TIME,
                    total_db_time,
                    {
                        "operation_count": len(db_operations),
                        "endpoint": request.url.path,
                    },
                )

            # Cache performance metrics if Redis is available
            if self.redis_client:
                cache_key = f"endpoint_metrics:{request.url.path}"
                metrics = {
                    "requests": 1,
                    "avg_response_time": processing_time,
                    "last_updated": datetime.utcnow().isoformat(),
                }

                # Update aggregated metrics
                existing = await self.redis_client.hget(cache_key, "data")
                if existing:
                    existing_data = json.loads(existing)
                    existing_data["requests"] += 1
                    existing_data["avg_response_time"] = (
                        existing_data["avg_response_time"]
                        * (existing_data["requests"] - 1)
                        + processing_time
                    ) / existing_data["requests"]
                    metrics = existing_data

                await self.redis_client.hset(cache_key, "data", json.dumps(metrics))
                await self.redis_client.expire(cache_key, 3600)  # 1 hour TTL

        except Exception as e:
            logger.error(f"Failed to record request metrics: {e}")

    async def _record_error_metrics(
        self, request: Request, error: str, processing_time: float
    ):
        """Record error metrics for monitoring"""
        try:
            await self.monitor.record_metric(
                MetricType.ERROR_RATE,
                1.0,
                {
                    "endpoint": request.url.path,
                    "method": request.method,
                    "error": error,
                    "processing_time": processing_time,
                },
            )

            # Alert on high error rates
            error_rate = await self._calculate_error_rate(request.url.path)
            if error_rate > 0.1:  # 10% error rate threshold
                await self.monitor.create_alert(
                    AlertLevel.ERROR,
                    MetricType.ERROR_RATE,
                    f"High error rate detected on {request.url.path}: {error_rate:.2%}",
                    error_rate,
                    0.1,
                )

        except Exception as e:
            logger.error(f"Failed to record error metrics: {e}")

    async def _calculate_error_rate(self, endpoint: str) -> float:
        """Calculate error rate for an endpoint"""
        if not self.redis_client:
            return 0.0

        try:
            # Get metrics from last hour
            end_time = datetime.utcnow()
            start_time = end_time - timedelta(hours=1)

            # This would typically query your metrics storage
            # For now, return a placeholder
            return 0.0

        except Exception as e:
            logger.error(f"Failed to calculate error rate: {e}")
            return 0.0

    async def _cleanup_request(self, request_id: str):
        """Cleanup request-specific resources"""
        try:
            # Remove from active requests tracking
            if self.redis_client:
                await self.redis_client.srem("active_requests", request_id)

        except Exception as e:
            logger.error(f"Failed to cleanup request {request_id}: {e}")


class DatabaseSessionMiddleware(BaseHTTPMiddleware):
    """
    Middleware for managing database sessions per request
    """

    def __init__(self, app, db_manager: DatabaseConnectionManager):
        super().__init__(app)
        self.db_manager = db_manager

    async def dispatch(self, request: Request, call_next):
        """Manage database session lifecycle"""
        session = None

        try:
            # Create session for database requests
            if self._requires_database(request):
                session = await self.db_manager.get_session()
                request.state.db = session

                # Track session metrics
                await self._track_session_start(session)

            response = await call_next(request)

            # Commit transaction if successful
            if session and response.status_code < 400:
                await session.commit()

            return response

        except Exception as e:
            # Rollback on error
            if session:
                await session.rollback()
                await self._track_session_error(session, str(e))
            raise e

        finally:
            # Always close session
            if session:
                await self._track_session_end(session)
                await session.close()

    def _requires_database(self, request: Request) -> bool:
        """Check if request requires database access"""
        database_paths = [
            "/api/database",
            "/api/chatbots",
            "/api/users",
            "/api/templates",
            "/api/auth",
        ]

        return any(request.url.path.startswith(path) for path in database_paths)

    async def _track_session_start(self, session: AsyncSession):
        """Track session start metrics"""
        try:
            # Record session creation
            session.info["start_time"] = time.time()
            session.info["query_count"] = 0

        except Exception as e:
            logger.error(f"Failed to track session start: {e}")

    async def _track_session_end(self, session: AsyncSession):
        """Track session end metrics"""
        try:
            start_time = session.info.get("start_time", time.time())
            duration = time.time() - start_time
            query_count = session.info.get("query_count", 0)

            # Log session metrics
            logger.debug(
                f"Session completed: duration={duration:.2f}s, queries={query_count}"
            )

        except Exception as e:
            logger.error(f"Failed to track session end: {e}")

    async def _track_session_error(self, session: AsyncSession, error: str):
        """Track session error metrics"""
        try:
            logger.warning(f"Session error: {error}")

        except Exception as e:
            logger.error(f"Failed to track session error: {e}")


class DatabaseCacheMiddleware(BaseHTTPMiddleware):
    """
    Middleware for database query result caching
    """

    def __init__(self, app, redis_url: str):
        super().__init__(app)
        self.redis_client: Optional[redis.Redis] = None
        self.redis_url = redis_url

    async def setup_redis(self):
        """Setup Redis connection"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url, encoding="utf-8", decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Redis cache middleware initialized")
        except Exception as e:
            logger.warning(f"Redis cache middleware failed to initialize: {e}")

    async def dispatch(self, request: Request, call_next):
        """Handle request with caching"""
        if not self.redis_client or not self._is_cacheable(request):
            return await call_next(request)

        cache_key = self._generate_cache_key(request)

        try:
            # Try to get from cache
            cached_response = await self.redis_client.get(cache_key)
            if cached_response:
                logger.debug(f"Cache hit for {cache_key}")
                response_data = json.loads(cached_response)

                response = Response(
                    content=response_data["content"],
                    status_code=response_data["status_code"],
                    headers=response_data["headers"],
                )
                response.headers["X-Cache"] = "HIT"
                return response

            # Process request
            response = await call_next(request)

            # Cache successful responses
            if response.status_code == 200 and hasattr(response, "body"):
                cache_data = {
                    "content": response.body.decode() if response.body else "",
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                }

                ttl = self._get_cache_ttl(request)
                await self.redis_client.setex(cache_key, ttl, json.dumps(cache_data))
                response.headers["X-Cache"] = "MISS"

            return response

        except Exception as e:
            logger.error(f"Cache middleware error: {e}")
            # Fallback to normal processing
            return await call_next(request)

    def _is_cacheable(self, request: Request) -> bool:
        """Check if request is cacheable"""
        # Only cache GET requests
        if request.method != "GET":
            return False

        # Cache specific endpoints
        cacheable_paths = [
            "/api/database/health",
            "/api/database/metrics",
            "/api/templates",
            "/api/chatbots",
        ]

        return any(request.url.path.startswith(path) for path in cacheable_paths)

    def _generate_cache_key(self, request: Request) -> str:
        """Generate cache key for request"""
        key_parts = [request.url.path, str(sorted(request.query_params.items()))]

        # Include user context if available
        if hasattr(request.state, "user_id"):
            key_parts.append(f"user:{request.state.user_id}")

        return "cache:" + ":".join(key_parts)

    def _get_cache_ttl(self, request: Request) -> int:
        """Get cache TTL based on request type"""
        ttl_map = {
            "/api/database/health": 30,  # 30 seconds
            "/api/database/metrics": 60,  # 1 minute
            "/api/templates": 300,  # 5 minutes
            "/api/chatbots": 180,  # 3 minutes
        }

        for path, ttl in ttl_map.items():
            if request.url.path.startswith(path):
                return ttl

        return 60  # Default 1 minute


async def setup_database_middleware(app, db_manager: DatabaseConnectionManager):
    """Setup all database middleware components"""

    # Add database monitoring middleware
    db_middleware = DatabaseMiddleware(app, db_manager)
    await db_middleware.setup_redis()
    app.add_middleware(DatabaseMiddleware, db_manager=db_manager)

    # Add session management middleware
    app.add_middleware(DatabaseSessionMiddleware, db_manager=db_manager)

    # Add caching middleware if Redis is available
    if settings.REDIS_URL:
        cache_middleware = DatabaseCacheMiddleware(app, settings.REDIS_URL)
        await cache_middleware.setup_redis()
        app.add_middleware(DatabaseCacheMiddleware, redis_url=settings.REDIS_URL)

    logger.info("Database middleware setup completed")


class DatabaseMetricsCollector:
    """
    Utility class for collecting database metrics across the application
    """

    def __init__(self, db_manager: DatabaseConnectionManager):
        self.db_manager = db_manager
        self.monitor = DatabaseMonitor(db_manager)

    async def collect_system_metrics(self) -> Dict[str, Any]:
        """Collect comprehensive system metrics"""
        try:
            # Get connection stats
            conn_stats = await self.db_manager.get_connection_stats()

            # Get database size
            async with self.db_manager.get_session() as session:
                size_query = text(
                    """
                    SELECT pg_size_pretty(pg_database_size(current_database())) as size,
                           pg_database_size(current_database()) as size_bytes
                """
                )
                result = await session.execute(size_query)
                size_data = result.fetchone()

                # Get table count
                table_query = text(
                    """
                    SELECT count(*) as table_count 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                """
                )
                result = await session.execute(table_query)
                table_count = result.scalar()

                # Get index count
                index_query = text(
                    """
                    SELECT count(*) as index_count 
                    FROM pg_indexes 
                    WHERE schemaname = 'public'
                """
                )
                result = await session.execute(index_query)
                index_count = result.scalar()

            return {
                "connections": conn_stats,
                "database_size": size_data[0] if size_data else "Unknown",
                "database_size_bytes": size_data[1] if size_data else 0,
                "table_count": table_count,
                "index_count": index_count,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return {}

    async def collect_performance_metrics(self) -> Dict[str, Any]:
        """Collect performance-related metrics"""
        try:
            async with self.db_manager.get_session() as session:
                # Slow queries
                slow_query = text(
                    """
                    SELECT query, calls, mean_time, total_time
                    FROM pg_stat_statements 
                    WHERE mean_time > 100 
                    ORDER BY mean_time DESC 
                    LIMIT 10
                """
                )
                result = await session.execute(slow_query)
                slow_queries = [dict(row) for row in result.fetchall()]

                # Cache hit ratio
                cache_query = text(
                    """
                    SELECT 
                        round(100 * sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)), 2) as cache_hit_ratio
                    FROM pg_statio_user_tables
                """
                )
                result = await session.execute(cache_query)
                cache_hit_ratio = result.scalar() or 0

                return {
                    "slow_queries": slow_queries,
                    "cache_hit_ratio": cache_hit_ratio,
                    "timestamp": datetime.utcnow().isoformat(),
                }

        except Exception as e:
            logger.error(f"Failed to collect performance metrics: {e}")
            return {}

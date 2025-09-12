"""
Database Connection Pool Manager
Advanced database connection management with pooling, monitoring, and optimization
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum

import asyncpg
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool, QueuePool
from sqlalchemy import event, text
from sqlalchemy.engine import Engine
from pydantic import BaseModel

try:
    from core.config import settings
except ImportError:
    from api.core.config import settings

logger = logging.getLogger(__name__)


class ConnectionStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    DOWN = "down"


@dataclass
class ConnectionStats:
    """Database connection statistics"""

    total_connections: int
    active_connections: int
    idle_connections: int
    waiting_connections: int
    max_connections: int
    connection_errors: int
    avg_response_time: float
    last_check: datetime
    status: ConnectionStatus


class DatabaseConfig(BaseModel):
    """Database configuration model"""

    host: str
    port: int
    database: str
    username: str
    password: str
    max_connections: int = 20
    min_connections: int = 5
    connection_timeout: int = 30
    idle_timeout: int = 300
    max_overflow: int = 10
    pool_pre_ping: bool = True
    pool_recycle: int = 3600
    echo: bool = False


class DatabaseConnectionManager:
    """Advanced database connection management with pooling and monitoring"""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine = None
        self.session_factory = None
        self.connection_stats = ConnectionStats(
            total_connections=0,
            active_connections=0,
            idle_connections=0,
            waiting_connections=0,
            max_connections=config.max_connections,
            connection_errors=0,
            avg_response_time=0.0,
            last_check=datetime.utcnow(),
            status=ConnectionStatus.DOWN,
        )
        self.query_times: List[float] = []
        self.max_query_history = 1000

    async def initialize(self):
        """Initialize database connection pool"""
        try:
            database_url = self._build_database_url()

            # Create engine with advanced pooling configuration
            self.engine = create_async_engine(
                database_url,
                poolclass=QueuePool,
                pool_size=self.config.max_connections,
                max_overflow=self.config.max_overflow,
                pool_pre_ping=self.config.pool_pre_ping,
                pool_recycle=self.config.pool_recycle,
                connect_args={
                    "command_timeout": self.config.connection_timeout,
                    "server_settings": {
                        "application_name": "pixel_ai_creator",
                        "timezone": "UTC",
                    },
                },
                echo=self.config.echo,
            )

            # Create async session factory
            self.session_factory = async_sessionmaker(
                self.engine, class_=AsyncSession, expire_on_commit=False
            )

            # Set up event listeners for monitoring
            self._setup_event_listeners()

            # Test connection
            await self._test_connection()

            logger.info("Database connection pool initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize database connection pool: {e}")
            raise

    def _build_database_url(self) -> str:
        """Build database URL from configuration"""
        return (
            f"postgresql+asyncpg://{self.config.username}:{self.config.password}"
            f"@{self.config.host}:{self.config.port}/{self.config.database}"
        )

    def _setup_event_listeners(self):
        """Set up SQLAlchemy event listeners for monitoring"""

        @event.listens_for(self.engine.sync_engine, "connect")
        def on_connect(dbapi_connection, connection_record):
            """Handle new connection"""
            self.connection_stats.total_connections += 1
            logger.debug("New database connection established")

        @event.listens_for(self.engine.sync_engine, "checkout")
        def on_checkout(dbapi_connection, connection_record, connection_proxy):
            """Handle connection checkout from pool"""
            self.connection_stats.active_connections += 1
            connection_record.info["checkout_time"] = time.time()

        @event.listens_for(self.engine.sync_engine, "checkin")
        def on_checkin(dbapi_connection, connection_record):
            """Handle connection checkin to pool"""
            if self.connection_stats.active_connections > 0:
                self.connection_stats.active_connections -= 1

            checkout_time = connection_record.info.get("checkout_time")
            if checkout_time:
                duration = time.time() - checkout_time
                self._record_query_time(duration)

    def _record_query_time(self, duration: float):
        """Record query execution time for analytics"""
        self.query_times.append(duration)

        # Keep only recent query times
        if len(self.query_times) > self.max_query_history:
            self.query_times = self.query_times[-self.max_query_history :]

        # Update average response time
        if self.query_times:
            self.connection_stats.avg_response_time = sum(self.query_times) / len(
                self.query_times
            )

    async def _test_connection(self):
        """Test database connectivity"""
        try:
            async with self.engine.begin() as conn:
                result = await conn.execute(text("SELECT 1"))
                result.fetchone()  # Remove await here

            self.connection_stats.status = ConnectionStatus.HEALTHY
            self.connection_stats.last_check = datetime.utcnow()

        except Exception as e:
            self.connection_stats.status = ConnectionStatus.DOWN
            self.connection_stats.connection_errors += 1
            logger.error(f"Database connection test failed: {e}")
            raise

    @asynccontextmanager
    async def get_session(self):
        """Get database session with proper error handling"""
        if not self.session_factory:
            raise RuntimeError("Database connection manager not initialized")

        session = self.session_factory()
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            await session.close()

    async def execute_query(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Execute a raw SQL query with monitoring"""
        start_time = time.time()

        try:
            async with self.engine.begin() as conn:
                result = await conn.execute(text(query), params or {})
                return await result.fetchall()

        except Exception as e:
            self.connection_stats.connection_errors += 1
            logger.error(f"Query execution failed: {e}")
            raise

        finally:
            duration = time.time() - start_time
            self._record_query_time(duration)

    async def get_connection_stats(self) -> ConnectionStats:
        """Get current connection pool statistics"""
        if self.engine:
            pool = self.engine.pool

            self.connection_stats.total_connections = pool.size()
            self.connection_stats.active_connections = pool.checkedout()
            self.connection_stats.idle_connections = pool.checkedin()
            self.connection_stats.waiting_connections = pool.overflow()

            # Determine connection status
            usage_ratio = (
                self.connection_stats.active_connections
                / self.connection_stats.max_connections
            )

            if usage_ratio < 0.7:
                self.connection_stats.status = ConnectionStatus.HEALTHY
            elif usage_ratio < 0.9:
                self.connection_stats.status = ConnectionStatus.WARNING
            else:
                self.connection_stats.status = ConnectionStatus.CRITICAL

        self.connection_stats.last_check = datetime.utcnow()
        return self.connection_stats

    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive database health check"""
        health_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "unknown",
            "connection_pool": {},
            "performance": {},
            "errors": [],
        }

        try:
            # Test basic connectivity
            await self._test_connection()

            # Get connection statistics
            stats = await self.get_connection_stats()

            health_data["connection_pool"] = {
                "total_connections": stats.total_connections,
                "active_connections": stats.active_connections,
                "idle_connections": stats.idle_connections,
                "max_connections": stats.max_connections,
                "usage_ratio": (
                    stats.active_connections / stats.max_connections
                    if stats.max_connections > 0
                    else 0
                ),
            }

            health_data["performance"] = {
                "avg_response_time_ms": stats.avg_response_time * 1000,
                "total_queries": len(self.query_times),
                "connection_errors": stats.connection_errors,
            }

            health_data["status"] = stats.status.value

        except Exception as e:
            health_data["status"] = "error"
            health_data["errors"].append(str(e))
            logger.error(f"Database health check failed: {e}")

        return health_data

    async def optimize_connections(self):
        """Optimize connection pool settings based on usage patterns"""
        stats = await self.get_connection_stats()

        recommendations = []

        # Analyze usage patterns
        usage_ratio = (
            stats.active_connections / stats.max_connections
            if stats.max_connections > 0
            else 0
        )

        if usage_ratio > 0.9:
            recommendations.append("Consider increasing max_connections")
        elif usage_ratio < 0.3:
            recommendations.append(
                "Consider decreasing max_connections to save resources"
            )

        if stats.avg_response_time > 1.0:  # 1 second
            recommendations.append(
                "High response time detected - consider query optimization"
            )

        if stats.connection_errors > 10:
            recommendations.append(
                "High error rate detected - investigate connection issues"
            )

        return {
            "current_stats": stats,
            "recommendations": recommendations,
            "optimized_settings": {
                "suggested_max_connections": min(
                    max(stats.active_connections * 2, 10), 50
                ),
                "suggested_pool_recycle": (
                    1800 if stats.avg_response_time > 0.5 else 3600
                ),
            },
        }

    async def close(self):
        """Close database connection pool"""
        if self.engine:
            await self.engine.dispose()
            logger.info("Database connection pool closed")


# Global connection manager instance
db_manager = None


async def get_db_manager() -> DatabaseConnectionManager:
    """Get or create database connection manager"""
    global db_manager

    if db_manager is None:
        config = DatabaseConfig(
            host=settings.DATABASE_HOST,
            port=settings.DATABASE_PORT,
            database=settings.DATABASE_NAME,
            username=settings.DATABASE_USER,
            password=settings.DATABASE_PASSWORD,
            max_connections=getattr(settings, "DATABASE_MAX_CONNECTIONS", 20),
            min_connections=getattr(settings, "DATABASE_MIN_CONNECTIONS", 5),
            connection_timeout=getattr(settings, "DATABASE_CONNECTION_TIMEOUT", 30),
            pool_pre_ping=getattr(settings, "DATABASE_POOL_PRE_PING", True),
            echo=getattr(settings, "DATABASE_ECHO", False),
        )

        db_manager = DatabaseConnectionManager(config)
        await db_manager.initialize()

    return db_manager


async def get_db_session():
    """Dependency to get database session"""
    manager = await get_db_manager()
    async with manager.get_session() as session:
        yield session

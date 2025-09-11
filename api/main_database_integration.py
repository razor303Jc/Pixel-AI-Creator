"""
Database Management Integration
Updates for main.py to integrate database management features
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from datetime import datetime

# Import existing modules
from api.core.database_manager import DatabaseConnectionManager
from api.services.database_monitor import DatabaseMonitor
from api.services.database_backup import DatabaseBackupService, DatabaseSecurity
from api.routes.database_management import router as database_router
from api.middleware.database_middleware import setup_database_middleware
from api.core.config import settings

logger = logging.getLogger(__name__)

# Global instances
db_manager: DatabaseConnectionManager = None
db_monitor: DatabaseMonitor = None
backup_service: DatabaseBackupService = None
security_service: DatabaseSecurity = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management with database setup"""
    global db_manager, db_monitor, backup_service, security_service

    try:
        # Initialize database manager
        logger.info("Initializing database management system...")

        db_manager = DatabaseConnectionManager(
            database_url=settings.DATABASE_URL,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_MAX_OVERFLOW,
            pool_timeout=settings.DB_POOL_TIMEOUT,
            pool_recycle=settings.DB_POOL_RECYCLE,
        )

        await db_manager.initialize()
        logger.info("Database connection manager initialized")

        # Initialize monitoring
        db_monitor = DatabaseMonitor(db_manager)
        await db_monitor.initialize()
        logger.info("Database monitoring system initialized")

        # Initialize backup service
        backup_service = DatabaseBackupService(
            db_manager=db_manager,
            backup_dir=settings.BACKUP_DIRECTORY,
            encryption_key=settings.BACKUP_ENCRYPTION_KEY,
            max_retention_days=settings.BACKUP_RETENTION_DAYS,
        )
        await backup_service.initialize()
        logger.info("Database backup service initialized")

        # Initialize security service
        security_service = DatabaseSecurity(
            db_manager=db_manager,
            audit_enabled=settings.DB_AUDIT_ENABLED,
            encryption_enabled=settings.DB_ENCRYPTION_ENABLED,
        )
        await security_service.initialize()
        logger.info("Database security service initialized")

        # Setup middleware
        await setup_database_middleware(app, db_manager)
        logger.info("Database middleware configured")

        # Start background tasks
        await start_background_tasks()
        logger.info("Background monitoring tasks started")

        # Perform initial health check
        health = await db_monitor.check_health()
        logger.info(f"Initial database health check: {health['status']}")

        yield

    except Exception as e:
        logger.error(f"Failed to initialize database management system: {e}")
        raise e

    finally:
        # Cleanup on shutdown
        logger.info("Shutting down database management system...")

        try:
            if backup_service:
                await backup_service.cleanup()

            if db_monitor:
                await db_monitor.stop_monitoring()

            if db_manager:
                await db_manager.close_all_connections()

            logger.info("Database management system shutdown complete")

        except Exception as e:
            logger.error(f"Error during database management shutdown: {e}")


async def start_background_tasks():
    """Start background monitoring and maintenance tasks"""

    # Start health monitoring
    if db_monitor:
        await db_monitor.start_continuous_monitoring(interval=30)  # Every 30 seconds
        logger.info("Continuous health monitoring started")

    # Schedule automatic backups
    if backup_service:
        await backup_service.schedule_backup(
            backup_type="incremental", schedule="0 */6 * * *"  # Every 6 hours
        )

        await backup_service.schedule_backup(
            backup_type="full",
            schedule="0 2 * * 0",  # Weekly full backup on Sunday at 2 AM
        )
        logger.info("Automatic backup scheduling configured")

    # Start security monitoring
    if security_service:
        await security_service.start_audit_monitoring()
        logger.info("Security audit monitoring started")


def create_application() -> FastAPI:
    """Create FastAPI application with database management"""

    app = FastAPI(
        title="Pixel AI Creator - Database Management",
        description="Advanced chatbot creation platform with comprehensive database management",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include database management routes
    app.include_router(database_router, prefix="/api", tags=["database-management"])

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        """Application health check including database status"""
        try:
            if not db_manager:
                return {
                    "status": "unhealthy",
                    "reason": "Database manager not initialized",
                }

            # Check database health
            health = (
                await db_monitor.check_health() if db_monitor else {"status": "unknown"}
            )

            # Check connection pool
            conn_stats = await db_manager.get_connection_stats()

            return {
                "status": "healthy",
                "timestamp": datetime.utcnow().isoformat(),
                "database": health,
                "connections": conn_stats,
                "services": {
                    "database_manager": bool(db_manager),
                    "monitoring": bool(db_monitor),
                    "backup": bool(backup_service),
                    "security": bool(security_service),
                },
            }

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "reason": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }

    # Database status endpoint
    @app.get("/api/status")
    async def database_status():
        """Detailed database status information"""
        try:
            if not db_manager or not db_monitor:
                raise HTTPException(
                    status_code=503, detail="Database services not available"
                )

            # Comprehensive status check
            health = await db_monitor.check_health()
            metrics = await db_monitor.get_current_metrics()
            alerts = await db_monitor.get_active_alerts()

            return {
                "health": health,
                "metrics": metrics,
                "active_alerts": len(alerts),
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"Database status check failed: {e}")
            raise HTTPException(status_code=500, detail="Status check failed")

    # Performance metrics endpoint
    @app.get("/api/metrics")
    async def performance_metrics():
        """Get current performance metrics"""
        try:
            if not db_monitor:
                raise HTTPException(
                    status_code=503, detail="Monitoring service not available"
                )

            return await db_monitor.get_performance_summary()

        except Exception as e:
            logger.error(f"Metrics retrieval failed: {e}")
            raise HTTPException(status_code=500, detail="Metrics unavailable")

    return app


# Dependency injection functions
async def get_database_manager() -> DatabaseConnectionManager:
    """Get database manager instance"""
    if not db_manager:
        raise HTTPException(status_code=503, detail="Database manager not available")
    return db_manager


async def get_database_monitor() -> DatabaseMonitor:
    """Get database monitor instance"""
    if not db_monitor:
        raise HTTPException(status_code=503, detail="Database monitor not available")
    return db_monitor


async def get_backup_service() -> DatabaseBackupService:
    """Get backup service instance"""
    if not backup_service:
        raise HTTPException(status_code=503, detail="Backup service not available")
    return backup_service


async def get_security_service() -> DatabaseSecurity:
    """Get security service instance"""
    if not security_service:
        raise HTTPException(status_code=503, detail="Security service not available")
    return security_service


# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions with database context"""
    logger.error(f"Unhandled exception in {request.url.path}: {exc}")

    # Record error in monitoring system
    if db_monitor:
        try:
            from api.services.database_monitor import MetricType

            await db_monitor.record_metric(
                MetricType.ERROR_RATE,
                1.0,
                {"endpoint": request.url.path, "error": str(exc)},
            )
        except Exception as e:
            logger.error(f"Failed to record error metric: {e}")

    return {
        "error": "Internal server error",
        "detail": "An unexpected error occurred",
        "timestamp": datetime.utcnow().isoformat(),
    }


# Create the application instance
app = create_application()

if __name__ == "__main__":
    import uvicorn

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Run the application
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
    )

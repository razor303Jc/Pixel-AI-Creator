"""
Database Monitoring and Health Check Service
Real-time monitoring, alerting, and performance analysis for database operations
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

from sqlalchemy import text
from pydantic import BaseModel

from core.database_manager import get_db_manager
from core.logging import get_logger

logger = get_logger(__name__)


class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class MetricType(Enum):
    CONNECTION_COUNT = "connection_count"
    RESPONSE_TIME = "response_time"
    ERROR_RATE = "error_rate"
    QUERY_COUNT = "query_count"
    DISK_USAGE = "disk_usage"
    MEMORY_USAGE = "memory_usage"


@dataclass
class DatabaseAlert:
    """Database alert information"""

    id: str
    level: AlertLevel
    metric_type: MetricType
    message: str
    value: float
    threshold: float
    timestamp: datetime
    resolved: bool = False


class DatabaseMetrics(BaseModel):
    """Database performance metrics"""

    timestamp: datetime
    connection_count: int
    active_connections: int
    idle_connections: int
    avg_response_time: float
    max_response_time: float
    min_response_time: float
    total_queries: int
    successful_queries: int
    failed_queries: int
    error_rate: float
    disk_usage_mb: float
    memory_usage_mb: float
    cpu_usage_percent: float


class DatabaseMonitor:
    """Advanced database monitoring and alerting system"""

    def __init__(self):
        self.metrics_history: List[DatabaseMetrics] = []
        self.active_alerts: List[DatabaseAlert] = []
        self.monitoring_enabled = True
        self.alert_thresholds = {
            MetricType.CONNECTION_COUNT: 80,  # 80% of max connections
            MetricType.RESPONSE_TIME: 1000,  # 1 second in milliseconds
            MetricType.ERROR_RATE: 5.0,  # 5% error rate
            MetricType.DISK_USAGE: 85.0,  # 85% disk usage
            MetricType.MEMORY_USAGE: 80.0,  # 80% memory usage
        }
        self.metrics_retention_hours = 24

    async def start_monitoring(self, interval_seconds: int = 60):
        """Start continuous database monitoring"""
        logger.info(f"Starting database monitoring with {interval_seconds}s interval")

        while self.monitoring_enabled:
            try:
                await self._collect_metrics()
                await self._check_thresholds()
                await self._cleanup_old_metrics()
                await asyncio.sleep(interval_seconds)

            except Exception as e:
                logger.error(f"Database monitoring error: {e}")
                await asyncio.sleep(interval_seconds)

    async def _collect_metrics(self):
        """Collect current database metrics"""
        try:
            db_manager = await get_db_manager()
            stats = await db_manager.get_connection_stats()

            # Get database-specific metrics
            db_metrics = await self._get_database_metrics()

            metrics = DatabaseMetrics(
                timestamp=datetime.utcnow(),
                connection_count=stats.active_connections,
                active_connections=stats.active_connections,
                idle_connections=stats.idle_connections,
                avg_response_time=stats.avg_response_time * 1000,  # Convert to ms
                max_response_time=db_metrics.get("max_response_time", 0),
                min_response_time=db_metrics.get("min_response_time", 0),
                total_queries=db_metrics.get("total_queries", 0),
                successful_queries=db_metrics.get("successful_queries", 0),
                failed_queries=stats.connection_errors,
                error_rate=self._calculate_error_rate(
                    stats.connection_errors, db_metrics.get("total_queries", 1)
                ),
                disk_usage_mb=db_metrics.get("disk_usage_mb", 0),
                memory_usage_mb=db_metrics.get("memory_usage_mb", 0),
                cpu_usage_percent=db_metrics.get("cpu_usage_percent", 0),
            )

            self.metrics_history.append(metrics)
            logger.debug(
                f"Collected metrics: {metrics.connection_count} connections, "
                f"{metrics.avg_response_time:.2f}ms avg response"
            )

        except Exception as e:
            logger.error(f"Failed to collect database metrics: {e}")

    async def _get_database_metrics(self) -> Dict[str, Any]:
        """Get database-specific performance metrics"""
        try:
            db_manager = await get_db_manager()

            # PostgreSQL-specific queries
            queries = {
                "connection_stats": """
                    SELECT count(*) as total_connections,
                           count(*) FILTER (WHERE state = 'active') as active,
                           count(*) FILTER (WHERE state = 'idle') as idle
                    FROM pg_stat_activity 
                    WHERE datname = current_database()
                """,
                "database_size": """
                    SELECT pg_size_pretty(pg_database_size(current_database())) as size,
                           pg_database_size(current_database()) as size_bytes
                """,
                "query_stats": """
                    SELECT sum(calls) as total_queries,
                           avg(mean_exec_time) as avg_time,
                           max(max_exec_time) as max_time,
                           min(min_exec_time) as min_time
                    FROM pg_stat_statements 
                    WHERE dbid = (SELECT oid FROM pg_database WHERE datname = current_database())
                """,
                "table_stats": """
                    SELECT schemaname, tablename, n_tup_ins, n_tup_upd, n_tup_del
                    FROM pg_stat_user_tables 
                    ORDER BY n_tup_ins + n_tup_upd + n_tup_del DESC 
                    LIMIT 10
                """,
            }

            results = {}

            for query_name, query in queries.items():
                try:
                    result = await db_manager.execute_query(query)
                    results[query_name] = result
                except Exception as e:
                    logger.warning(f"Failed to execute {query_name}: {e}")
                    results[query_name] = []

            # Process results into metrics
            metrics = {
                "total_queries": 0,
                "successful_queries": 0,
                "max_response_time": 0,
                "min_response_time": 0,
                "disk_usage_mb": 0,
                "memory_usage_mb": 0,
                "cpu_usage_percent": 0,
            }

            # Extract query statistics
            if results.get("query_stats") and len(results["query_stats"]) > 0:
                query_stat = results["query_stats"][0]
                metrics["total_queries"] = query_stat.get("total_queries", 0) or 0
                metrics["max_response_time"] = query_stat.get("max_time", 0) or 0
                metrics["min_response_time"] = query_stat.get("min_time", 0) or 0

            # Extract database size
            if results.get("database_size") and len(results["database_size"]) > 0:
                size_stat = results["database_size"][0]
                size_bytes = size_stat.get("size_bytes", 0) or 0
                metrics["disk_usage_mb"] = size_bytes / (1024 * 1024)  # Convert to MB

            return metrics

        except Exception as e:
            logger.error(f"Failed to get database metrics: {e}")
            return {}

    def _calculate_error_rate(self, errors: int, total: int) -> float:
        """Calculate error rate percentage"""
        if total <= 0:
            return 0.0
        return (errors / total) * 100

    async def _check_thresholds(self):
        """Check metrics against alert thresholds"""
        if not self.metrics_history:
            return

        latest_metrics = self.metrics_history[-1]

        # Check connection count threshold
        if (
            latest_metrics.connection_count
            > self.alert_thresholds[MetricType.CONNECTION_COUNT]
        ):
            await self._create_alert(
                AlertLevel.WARNING,
                MetricType.CONNECTION_COUNT,
                f"High connection count: {latest_metrics.connection_count}",
                latest_metrics.connection_count,
                self.alert_thresholds[MetricType.CONNECTION_COUNT],
            )

        # Check response time threshold
        if (
            latest_metrics.avg_response_time
            > self.alert_thresholds[MetricType.RESPONSE_TIME]
        ):
            await self._create_alert(
                AlertLevel.WARNING,
                MetricType.RESPONSE_TIME,
                f"High response time: {latest_metrics.avg_response_time:.2f}ms",
                latest_metrics.avg_response_time,
                self.alert_thresholds[MetricType.RESPONSE_TIME],
            )

        # Check error rate threshold
        if latest_metrics.error_rate > self.alert_thresholds[MetricType.ERROR_RATE]:
            level = (
                AlertLevel.CRITICAL
                if latest_metrics.error_rate > 10
                else AlertLevel.ERROR
            )
            await self._create_alert(
                level,
                MetricType.ERROR_RATE,
                f"High error rate: {latest_metrics.error_rate:.2f}%",
                latest_metrics.error_rate,
                self.alert_thresholds[MetricType.ERROR_RATE],
            )

        # Check disk usage threshold
        if latest_metrics.disk_usage_mb > 0:
            disk_usage_percent = (
                latest_metrics.disk_usage_mb / 1024
            ) * 100  # Assume 1GB limit
            if disk_usage_percent > self.alert_thresholds[MetricType.DISK_USAGE]:
                await self._create_alert(
                    AlertLevel.WARNING,
                    MetricType.DISK_USAGE,
                    f"High disk usage: {disk_usage_percent:.1f}%",
                    disk_usage_percent,
                    self.alert_thresholds[MetricType.DISK_USAGE],
                )

    async def _create_alert(
        self,
        level: AlertLevel,
        metric_type: MetricType,
        message: str,
        value: float,
        threshold: float,
    ):
        """Create a new alert"""
        alert_id = f"{metric_type.value}_{int(time.time())}"

        alert = DatabaseAlert(
            id=alert_id,
            level=level,
            metric_type=metric_type,
            message=message,
            value=value,
            threshold=threshold,
            timestamp=datetime.utcnow(),
        )

        self.active_alerts.append(alert)
        logger.warning(f"Database alert created: {alert.level.value} - {alert.message}")

        # TODO: Implement alert notification system (email, Slack, etc.)

    async def _cleanup_old_metrics(self):
        """Remove old metrics to prevent memory buildup"""
        cutoff_time = datetime.utcnow() - timedelta(hours=self.metrics_retention_hours)

        self.metrics_history = [
            m for m in self.metrics_history if m.timestamp > cutoff_time
        ]

        # Also cleanup resolved alerts older than 24 hours
        alert_cutoff = datetime.utcnow() - timedelta(hours=24)
        self.active_alerts = [
            a
            for a in self.active_alerts
            if not a.resolved or a.timestamp > alert_cutoff
        ]

    async def get_current_metrics(self) -> Optional[DatabaseMetrics]:
        """Get the most recent metrics"""
        return self.metrics_history[-1] if self.metrics_history else None

    async def get_metrics_history(self, hours: int = 24) -> List[DatabaseMetrics]:
        """Get metrics history for specified time period"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        return [m for m in self.metrics_history if m.timestamp > cutoff_time]

    async def get_active_alerts(self) -> List[DatabaseAlert]:
        """Get all active (unresolved) alerts"""
        return [a for a in self.active_alerts if not a.resolved]

    async def resolve_alert(self, alert_id: str) -> bool:
        """Mark an alert as resolved"""
        for alert in self.active_alerts:
            if alert.id == alert_id:
                alert.resolved = True
                logger.info(f"Alert resolved: {alert_id}")
                return True
        return False

    async def get_health_summary(self) -> Dict[str, Any]:
        """Get overall database health summary"""
        current_metrics = await self.get_current_metrics()
        active_alerts = await self.get_active_alerts()

        if not current_metrics:
            return {"status": "unknown", "message": "No metrics available"}

        # Determine overall health status
        critical_alerts = [a for a in active_alerts if a.level == AlertLevel.CRITICAL]
        error_alerts = [a for a in active_alerts if a.level == AlertLevel.ERROR]
        warning_alerts = [a for a in active_alerts if a.level == AlertLevel.WARNING]

        if critical_alerts:
            status = "critical"
            message = f"{len(critical_alerts)} critical alert(s) active"
        elif error_alerts:
            status = "error"
            message = f"{len(error_alerts)} error alert(s) active"
        elif warning_alerts:
            status = "warning"
            message = f"{len(warning_alerts)} warning alert(s) active"
        else:
            status = "healthy"
            message = "All metrics within normal ranges"

        return {
            "status": status,
            "message": message,
            "metrics": {
                "connections": current_metrics.connection_count,
                "avg_response_time_ms": current_metrics.avg_response_time,
                "error_rate_percent": current_metrics.error_rate,
                "total_queries": current_metrics.total_queries,
            },
            "alerts": {
                "critical": len(critical_alerts),
                "error": len(error_alerts),
                "warning": len(warning_alerts),
                "total": len(active_alerts),
            },
            "timestamp": current_metrics.timestamp.isoformat(),
        }

    def stop_monitoring(self):
        """Stop database monitoring"""
        self.monitoring_enabled = False
        logger.info("Database monitoring stopped")


# Global monitor instance
db_monitor = DatabaseMonitor()

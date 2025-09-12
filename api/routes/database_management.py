"""
Database Management API Routes
RESTful endpoints for database monitoring, backup, and administration
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel

from core.database_manager import get_db_manager, ConnectionStats
from services.database_monitor import db_monitor, DatabaseMetrics, DatabaseAlert
from services.database_backup import (
    backup_service,
    security_service,
    BackupType,
    BackupInfo,
)

# from auth.jwt import verify_user_token
# from models.database_schema import User

router = APIRouter()


# Response Models
class ConnectionStatsResponse(BaseModel):
    total_connections: int
    active_connections: int
    idle_connections: int
    waiting_connections: int
    max_connections: int
    connection_errors: int
    avg_response_time: float
    status: str


class DatabaseHealthResponse(BaseModel):
    status: str
    message: str
    metrics: Dict[str, Any]
    alerts: Dict[str, int]
    timestamp: str


class BackupRequest(BaseModel):
    backup_type: str = "full"
    custom_name: Optional[str] = None


class BackupResponse(BaseModel):
    id: str
    backup_type: str
    file_size: int
    status: str
    created_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]
    encrypted: bool


class MetricsResponse(BaseModel):
    timestamp: datetime
    connection_count: int
    avg_response_time: float
    error_rate: float
    total_queries: int


class AlertResponse(BaseModel):
    id: str
    level: str
    metric_type: str
    message: str
    value: float
    threshold: float
    timestamp: datetime
    resolved: bool


# Database Connection Management Endpoints


@router.get("/health", response_model=DatabaseHealthResponse)
async def get_database_health():
    """Get comprehensive database health status"""
    try:
        health_summary = await db_monitor.get_health_summary()
        return DatabaseHealthResponse(**health_summary)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@router.get("/connections/stats", response_model=ConnectionStatsResponse)
async def get_connection_stats(current_user: User = Depends(get_current_user)):
    """Get current database connection pool statistics"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        db_manager = await get_db_manager()
        stats = await db_manager.get_connection_stats()

        return ConnectionStatsResponse(
            total_connections=stats.total_connections,
            active_connections=stats.active_connections,
            idle_connections=stats.idle_connections,
            waiting_connections=stats.waiting_connections,
            max_connections=stats.max_connections,
            connection_errors=stats.connection_errors,
            avg_response_time=stats.avg_response_time,
            status=stats.status.value,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get connection stats: {str(e)}"
        )


@router.get("/connections/optimize")
async def optimize_connections(current_user: User = Depends(get_current_user)):
    """Get connection pool optimization recommendations"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        db_manager = await get_db_manager()
        optimization_data = await db_manager.optimize_connections()
        return optimization_data
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Optimization analysis failed: {str(e)}"
        )


# Database Monitoring Endpoints


@router.get("/metrics/current", response_model=MetricsResponse)
async def get_current_metrics(current_user: User = Depends(get_current_user)):
    """Get current database performance metrics"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        current_metrics = await db_monitor.get_current_metrics()
        if not current_metrics:
            raise HTTPException(status_code=404, detail="No metrics available")

        return MetricsResponse(
            timestamp=current_metrics.timestamp,
            connection_count=current_metrics.connection_count,
            avg_response_time=current_metrics.avg_response_time,
            error_rate=current_metrics.error_rate,
            total_queries=current_metrics.total_queries,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")


@router.get("/metrics/history", response_model=List[MetricsResponse])
async def get_metrics_history(
    hours: int = 24, current_user: User = Depends(get_current_user)
):
    """Get database metrics history for specified time period"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    if hours > 168:  # 1 week limit
        raise HTTPException(
            status_code=400, detail="Maximum 168 hours (1 week) allowed"
        )

    try:
        metrics_history = await db_monitor.get_metrics_history(hours)
        return [
            MetricsResponse(
                timestamp=m.timestamp,
                connection_count=m.connection_count,
                avg_response_time=m.avg_response_time,
                error_rate=m.error_rate,
                total_queries=m.total_queries,
            )
            for m in metrics_history
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get metrics history: {str(e)}"
        )


@router.get("/alerts", response_model=List[AlertResponse])
async def get_active_alerts(current_user: User = Depends(get_current_user)):
    """Get all active database alerts"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        active_alerts = await db_monitor.get_active_alerts()
        return [
            AlertResponse(
                id=alert.id,
                level=alert.level.value,
                metric_type=alert.metric_type.value,
                message=alert.message,
                value=alert.value,
                threshold=alert.threshold,
                timestamp=alert.timestamp,
                resolved=alert.resolved,
            )
            for alert in active_alerts
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get alerts: {str(e)}")


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str, current_user: User = Depends(get_current_user)):
    """Mark an alert as resolved"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        success = await db_monitor.resolve_alert(alert_id)
        if not success:
            raise HTTPException(status_code=404, detail="Alert not found")

        return {"message": "Alert resolved successfully", "alert_id": alert_id}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to resolve alert: {str(e)}"
        )


# Database Backup Endpoints


@router.post("/backups", response_model=BackupResponse)
async def create_backup(
    backup_request: BackupRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
):
    """Create a new database backup"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        # Validate backup type
        backup_type = BackupType(backup_request.backup_type.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid backup type. Must be one of: {[t.value for t in BackupType]}",
        )

    try:
        # Create backup in background
        backup_info = await backup_service.create_backup(
            backup_type, backup_request.custom_name
        )

        return BackupResponse(
            id=backup_info.id,
            backup_type=backup_info.backup_type.value,
            file_size=backup_info.file_size,
            status=backup_info.status.value,
            created_at=backup_info.created_at,
            completed_at=backup_info.completed_at,
            error_message=backup_info.error_message,
            encrypted=backup_info.encrypted,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backup creation failed: {str(e)}")


@router.get("/backups", response_model=List[BackupResponse])
async def list_backups(current_user: User = Depends(get_current_user)):
    """List all available backups"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        backups = await backup_service.list_backups()
        return [
            BackupResponse(
                id=backup.id,
                backup_type=backup.backup_type.value,
                file_size=backup.file_size,
                status=backup.status.value,
                created_at=backup.created_at,
                completed_at=backup.completed_at,
                error_message=backup.error_message,
                encrypted=backup.encrypted,
            )
            for backup in backups
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list backups: {str(e)}")


@router.get("/backups/{backup_id}", response_model=BackupResponse)
async def get_backup_info(
    backup_id: str, current_user: User = Depends(get_current_user)
):
    """Get detailed information about a specific backup"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        backup_info = await backup_service.get_backup_info(backup_id)
        if not backup_info:
            raise HTTPException(status_code=404, detail="Backup not found")

        return BackupResponse(
            id=backup_info.id,
            backup_type=backup_info.backup_type.value,
            file_size=backup_info.file_size,
            status=backup_info.status.value,
            created_at=backup_info.created_at,
            completed_at=backup_info.completed_at,
            error_message=backup_info.error_message,
            encrypted=backup_info.encrypted,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get backup info: {str(e)}"
        )


@router.post("/backups/{backup_id}/restore")
async def restore_backup(
    backup_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
):
    """Restore database from backup"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        # Perform restore in background
        success = await backup_service.restore_backup(backup_id)

        if success:
            # Log the restore action
            await security_service.audit_user_access(
                str(current_user.id),
                "DATABASE_RESTORE",
                "system",
                {"backup_id": backup_id},
            )

            return {"message": "Database restored successfully", "backup_id": backup_id}
        else:
            raise HTTPException(status_code=500, detail="Restore failed")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Restore failed: {str(e)}")


@router.delete("/backups/{backup_id}")
async def delete_backup(backup_id: str, current_user: User = Depends(get_current_user)):
    """Delete a specific backup"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        success = await backup_service.delete_backup(backup_id)
        if not success:
            raise HTTPException(status_code=404, detail="Backup not found")

        # Log the deletion
        await security_service.audit_user_access(
            str(current_user.id), "BACKUP_DELETION", "system", {"backup_id": backup_id}
        )

        return {"message": "Backup deleted successfully", "backup_id": backup_id}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete backup: {str(e)}"
        )


# Database Security Endpoints


@router.get("/security/audit")
async def get_audit_report(
    start_date: datetime,
    end_date: datetime,
    current_user: User = Depends(get_current_user),
):
    """Get database audit report for specified date range"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    if end_date <= start_date:
        raise HTTPException(status_code=400, detail="End date must be after start date")

    if (end_date - start_date).days > 90:
        raise HTTPException(status_code=400, detail="Maximum 90 days range allowed")

    try:
        audit_report = await security_service.get_audit_report(start_date, end_date)
        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_entries": len(audit_report),
            "audit_entries": audit_report,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate audit report: {str(e)}"
        )


@router.post("/security/anonymize")
async def anonymize_data(
    table: str, column: str, current_user: User = Depends(get_current_user)
):
    """Anonymize sensitive data in specified table/column"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    # Security check - only allow specific tables/columns
    allowed_tables = ["users", "clients", "conversations"]
    allowed_columns = ["email", "phone", "notes", "metadata"]

    if table not in allowed_tables:
        raise HTTPException(
            status_code=400, detail=f"Table not allowed for anonymization: {table}"
        )

    if column not in allowed_columns:
        raise HTTPException(
            status_code=400, detail=f"Column not allowed for anonymization: {column}"
        )

    try:
        success = await security_service.anonymize_sensitive_data(table, column)
        if success:
            return {
                "message": f"Data anonymized successfully in {table}.{column}",
                "table": table,
                "column": column,
            }
        else:
            raise HTTPException(status_code=500, detail="Anonymization failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Anonymization failed: {str(e)}")


# Database Administration Dashboard


@router.get("/dashboard")
async def get_database_dashboard(current_user: User = Depends(get_current_user)):
    """Get comprehensive database management dashboard data"""
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    try:
        # Gather all dashboard data
        health_summary = await db_monitor.get_health_summary()
        current_metrics = await db_monitor.get_current_metrics()
        active_alerts = await db_monitor.get_active_alerts()
        recent_backups = await backup_service.list_backups()

        db_manager = await get_db_manager()
        connection_stats = await db_manager.get_connection_stats()

        dashboard_data = {
            "health": health_summary,
            "current_metrics": current_metrics.dict() if current_metrics else None,
            "connection_stats": {
                "total": connection_stats.total_connections,
                "active": connection_stats.active_connections,
                "idle": connection_stats.idle_connections,
                "usage_percent": (
                    (
                        connection_stats.active_connections
                        / connection_stats.max_connections
                        * 100
                    )
                    if connection_stats.max_connections > 0
                    else 0
                ),
            },
            "alerts": {
                "total": len(active_alerts),
                "critical": len(
                    [a for a in active_alerts if a.level.value == "critical"]
                ),
                "warning": len(
                    [a for a in active_alerts if a.level.value == "warning"]
                ),
            },
            "backups": {
                "total": len(recent_backups),
                "recent": recent_backups[:5],  # Last 5 backups
                "last_backup": recent_backups[0].created_at if recent_backups else None,
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

        return dashboard_data

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Dashboard data retrieval failed: {str(e)}"
        )

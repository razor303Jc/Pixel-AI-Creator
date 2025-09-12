"""
Simple Database Management API Routes (No Auth for Testing)
"""

from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.database_manager import get_db_manager

router = APIRouter()


# Response Models
class DatabaseStatsResponse(BaseModel):
    total_connections: int
    active_connections: int
    idle_connections: int
    timestamp: datetime


# Routes
@router.get("/stats", response_model=DatabaseStatsResponse)
async def get_connection_stats():
    """Get current database connection statistics."""
    try:
        db_manager = await get_db_manager()
        stats = await db_manager.get_connection_stats()

        return DatabaseStatsResponse(
            total_connections=stats.total_connections,
            active_connections=stats.active_connections,
            idle_connections=stats.idle_connections,
            timestamp=datetime.utcnow(),
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get connection stats: {str(e)}"
        )


@router.get("/health")
async def database_health():
    """Check database health status."""
    try:
        db_manager = await get_db_manager()
        is_healthy = await db_manager.health_check()

        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "service": "database-management",
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
            "service": "database-management",
        }

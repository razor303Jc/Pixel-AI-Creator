"""
Performance optimization API routes for Pixel AI Creator.

Provides endpoints for caching management, background task monitoring,
and analytics access.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import asyncio

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from core.database import get_db
from auth.middleware import get_current_user
from services.cache_service import RedisCache
from services.background_tasks import TaskManager
from services.conversation_processor import (
    ConversationProcessor,
    PriorityConversationProcessor,
    BatchConversationProcessor,
)
from services.analytics_processor import AnalyticsProcessor
from models.user import User

router = APIRouter(prefix="/performance", tags=["performance"])


# Cache management endpoints
@router.get("/cache/stats")
async def get_cache_stats(current_user: User = Depends(get_current_user)):
    """Get cache statistics and performance metrics."""
    try:
        cache_service = CacheService()
        stats = await cache_service.get_stats()

        return {
            "status": "success",
            "cache_stats": stats,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get cache stats: {str(e)}"
        )


@router.post("/cache/clear")
async def clear_cache(
    pattern: Optional[str] = None, current_user: User = Depends(get_current_user)
):
    """Clear cache entries by pattern."""
    try:
        cache_service = CacheService()

        if pattern:
            cleared_count = await cache_service.delete_pattern(pattern)
        else:
            # Clear all cache (use with caution)
            cleared_count = await cache_service.clear_all()

        return {
            "status": "success",
            "cleared_entries": cleared_count,
            "pattern": pattern,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to clear cache: {str(e)}")


@router.get("/cache/key/{key}")
async def get_cache_entry(key: str, current_user: User = Depends(get_current_user)):
    """Get specific cache entry by key."""
    try:
        cache_service = CacheService()
        value = await cache_service.get(key)

        if value is None:
            raise HTTPException(status_code=404, detail=f"Cache key '{key}' not found")

        return {
            "status": "success",
            "key": key,
            "value": value,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get cache entry: {str(e)}"
        )


@router.delete("/cache/key/{key}")
async def delete_cache_entry(key: str, current_user: User = Depends(get_current_user)):
    """Delete specific cache entry by key."""
    try:
        cache_service = CacheService()
        deleted = await cache_service.delete(key)

        return {
            "status": "success",
            "deleted": deleted,
            "key": key,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete cache entry: {str(e)}"
        )


# Background task management endpoints
@router.get("/tasks/active")
async def get_active_tasks(current_user: User = Depends(get_current_user)):
    """Get list of active background tasks."""
    try:
        active_tasks = TaskManager.get_active_tasks()

        return {
            "status": "success",
            "active_tasks": active_tasks,
            "task_count": len(active_tasks),
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get active tasks: {str(e)}"
        )


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str, current_user: User = Depends(get_current_user)):
    """Get status of specific background task."""
    try:
        task_status = TaskManager.get_task_status(task_id)

        return {
            "status": "success",
            "task_status": task_status,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get task status: {str(e)}"
        )


@router.delete("/tasks/{task_id}")
async def cancel_task(task_id: str, current_user: User = Depends(get_current_user)):
    """Cancel a running background task."""
    try:
        cancelled = TaskManager.cancel_task(task_id)

        return {
            "status": "success",
            "cancelled": cancelled,
            "task_id": task_id,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cancel task: {str(e)}")


# Conversation processing endpoints
@router.post("/conversations/queue")
async def queue_conversation(
    conversation_data: Dict[str, Any],
    priority: str = "normal",
    current_user: User = Depends(get_current_user),
):
    """Queue a conversation for background processing."""
    try:
        processor = ConversationProcessor()

        task_id = await processor.queue_conversation(
            conversation_data["conversation_id"],
            conversation_data["user_message"],
            conversation_data["bot_id"],
            str(current_user.id),
            priority,
        )

        return {
            "status": "success",
            "task_id": task_id,
            "conversation_id": conversation_data["conversation_id"],
            "priority": priority,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to queue conversation: {str(e)}"
        )


@router.post("/conversations/queue/priority")
async def queue_priority_conversation(
    conversation_data: Dict[str, Any], current_user: User = Depends(get_current_user)
):
    """Queue a high-priority conversation for immediate processing."""
    try:
        processor = PriorityConversationProcessor()

        task_id = await processor.queue_priority_conversation(
            conversation_data["conversation_id"],
            conversation_data["user_message"],
            conversation_data["bot_id"],
            str(current_user.id),
        )

        return {
            "status": "success",
            "task_id": task_id,
            "conversation_id": conversation_data["conversation_id"],
            "priority": "high",
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to queue priority conversation: {str(e)}"
        )


@router.post("/conversations/batch")
async def process_conversation_batch(
    batch_data: Dict[str, Any], current_user: User = Depends(get_current_user)
):
    """Process a batch of conversations."""
    try:
        processor = BatchConversationProcessor()

        # Add user_id to each conversation in batch
        for conversation in batch_data["conversations"]:
            conversation["user_id"] = str(current_user.id)

        result = await processor.process_conversation_batch(
            batch_data["conversations"], batch_data["batch_id"]
        )

        return {
            "status": "success",
            "batch_result": result,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to process conversation batch: {str(e)}"
        )


@router.get("/conversations/{conversation_id}/status")
async def get_conversation_status(
    conversation_id: str, current_user: User = Depends(get_current_user)
):
    """Get status of conversation processing."""
    try:
        processor = ConversationProcessor()
        status = await processor.get_conversation_status(conversation_id)

        return {
            "status": "success",
            "conversation_status": status,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get conversation status: {str(e)}"
        )


@router.get("/conversations/batch/{batch_id}/status")
async def get_batch_status(
    batch_id: str, current_user: User = Depends(get_current_user)
):
    """Get status of conversation batch processing."""
    try:
        processor = BatchConversationProcessor()
        status = await processor.get_batch_status(batch_id)

        return {
            "status": "success",
            "batch_status": status,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get batch status: {str(e)}"
        )


@router.get("/conversations/metrics")
async def get_conversation_metrics(current_user: User = Depends(get_current_user)):
    """Get conversation processing metrics."""
    try:
        processor = ConversationProcessor()
        metrics = await processor.get_conversation_metrics()

        return {
            "status": "success",
            "metrics": metrics,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get conversation metrics: {str(e)}"
        )


# Analytics endpoints
@router.get("/analytics/daily")
async def get_daily_analytics(
    date: Optional[str] = None, current_user: User = Depends(get_current_user)
):
    """Get daily analytics report."""
    try:
        processor = AnalyticsProcessor()

        if date:
            target_date = datetime.fromisoformat(date).date()
        else:
            target_date = datetime.utcnow().date() - timedelta(days=1)

        analytics = await processor.generate_daily_analytics(target_date)

        return {
            "status": "success",
            "analytics": analytics,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get daily analytics: {str(e)}"
        )


@router.get("/analytics/weekly")
async def get_weekly_analytics(
    date: Optional[str] = None, current_user: User = Depends(get_current_user)
):
    """Get weekly analytics report."""
    try:
        processor = AnalyticsProcessor()

        if date:
            target_date = datetime.fromisoformat(date)
        else:
            target_date = datetime.utcnow() - timedelta(days=7)

        analytics = await processor.generate_weekly_analytics(target_date)

        return {
            "status": "success",
            "analytics": analytics,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get weekly analytics: {str(e)}"
        )


@router.get("/analytics/monthly")
async def get_monthly_analytics(
    date: Optional[str] = None, current_user: User = Depends(get_current_user)
):
    """Get monthly analytics report."""
    try:
        processor = AnalyticsProcessor()

        if date:
            target_date = datetime.fromisoformat(date)
        else:
            target_date = datetime.utcnow() - timedelta(days=30)

        analytics = await processor.generate_monthly_analytics(target_date)

        return {
            "status": "success",
            "analytics": analytics,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get monthly analytics: {str(e)}"
        )


@router.post("/analytics/generate")
async def trigger_analytics_generation(
    report_type: str,
    date_range: Dict[str, str],
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
):
    """Trigger analytics generation for specific date range."""
    try:
        from services.background_tasks import generate_analytics_task

        # Queue analytics generation task
        task = generate_analytics_task.apply_async(
            args=[report_type, date_range["start_date"], date_range["end_date"]],
            queue="analytics",
        )

        return {
            "status": "success",
            "task_id": task.id,
            "report_type": report_type,
            "date_range": date_range,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to trigger analytics generation: {str(e)}"
        )


# System health endpoints
@router.get("/health")
async def get_system_health(current_user: User = Depends(get_current_user)):
    """Get current system health status."""
    try:
        cache_service = CacheService()
        health_report = await cache_service.get("system:health")

        if not health_report:
            # Generate fresh health report
            from services.background_tasks import generate_system_health_report

            task = generate_system_health_report.apply_async(queue="maintenance")
            health_report = {"status": "generating", "task_id": task.id}

        return {
            "status": "success",
            "health_report": health_report,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get system health: {str(e)}"
        )


@router.post("/maintenance/cleanup")
async def trigger_maintenance_cleanup(
    cleanup_type: str = "all", current_user: User = Depends(get_current_user)
):
    """Trigger system maintenance and cleanup tasks."""
    try:
        task_ids = []

        if cleanup_type in ["all", "conversations"]:
            from services.background_tasks import cleanup_old_conversations

            task = cleanup_old_conversations.apply_async(queue="maintenance")
            task_ids.append({"type": "conversations", "task_id": task.id})

        if cleanup_type in ["all", "cache"]:
            cache_service = CacheService()
            cleaned = await cache_service.cleanup_expired()
            task_ids.append({"type": "cache", "cleaned_keys": cleaned})

        return {
            "status": "success",
            "cleanup_tasks": task_ids,
            "cleanup_type": cleanup_type,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to trigger maintenance cleanup: {str(e)}"
        )


@router.get("/performance/summary")
async def get_performance_summary(current_user: User = Depends(get_current_user)):
    """Get comprehensive performance summary."""
    try:
        cache_service = CacheService()

        # Get cache stats
        cache_stats = await cache_service.get_stats()

        # Get conversation metrics
        conv_processor = ConversationProcessor()
        conv_metrics = await conv_processor.get_conversation_metrics()

        # Get system health
        health_report = await cache_service.get("system:health") or {}

        # Get active tasks
        active_tasks = TaskManager.get_active_tasks()

        summary = {
            "cache_performance": cache_stats,
            "conversation_metrics": conv_metrics,
            "system_health": health_report,
            "active_tasks_count": len(active_tasks),
            "performance_score": await _calculate_performance_score(
                cache_stats, conv_metrics, health_report
            ),
            "timestamp": datetime.utcnow().isoformat(),
        }

        return {
            "status": "success",
            "performance_summary": summary,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get performance summary: {str(e)}"
        )


async def _calculate_performance_score(
    cache_stats: Dict[str, Any],
    conv_metrics: Dict[str, Any],
    health_report: Dict[str, Any],
) -> float:
    """Calculate overall performance score."""
    try:
        score = 100.0

        # Cache performance impact
        cache_hit_rate = cache_stats.get("hit_rate", 0)
        if cache_hit_rate < 80:
            score -= (80 - cache_hit_rate) * 0.5

        # Conversation success rate impact
        success_rate = conv_metrics.get("success_rate", 0)
        if success_rate < 95:
            score -= (95 - success_rate) * 0.3

        # System health impact
        cpu_usage = health_report.get("system", {}).get("cpu_percent", 0)
        memory_usage = health_report.get("system", {}).get("memory_percent", 0)

        if cpu_usage > 80:
            score -= (cpu_usage - 80) * 0.2

        if memory_usage > 85:
            score -= (memory_usage - 85) * 0.3

        return max(0, min(100, score))

    except Exception:
        return 50.0  # Default score if calculation fails

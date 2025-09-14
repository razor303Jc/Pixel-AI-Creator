"""
Celery configuration for background job processing in Pixel AI Creator.

Handles async conversation processing, scheduled analytics generation,
and other background tasks.
"""

import os
from celery import Celery
from celery.schedules import crontab
from kombu import Queue

from core.config import get_settings

settings = get_settings()

# Create Celery instance
celery_app = Celery(
    "pixel_ai_creator",
    broker=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/1",
    backend=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/2",
    include=[
        "services.background_tasks",
        # "services.analytics_processor",  # Temporarily disabled due to import issues
        # "services.conversation_processor",  # Temporarily disabled due to import issues
    ],
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Task routing
    task_routes={
        # "services.analytics_processor.*": {"queue": "analytics"},
        # "services.conversation_processor.*": {"queue": "conversations"},
        "services.background_tasks.send_email": {"queue": "notifications"},
        "services.background_tasks.cleanup_*": {"queue": "maintenance"},
    },
    # Queue configuration
    task_default_queue="default",
    task_queues=(
        Queue("default"),
        Queue("analytics", routing_key="analytics"),
        Queue("conversations", routing_key="conversations"),
        Queue("notifications", routing_key="notifications"),
        Queue("maintenance", routing_key="maintenance"),
    ),
    # Worker settings
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
    # Task execution settings
    task_soft_time_limit=300,  # 5 minutes
    task_time_limit=600,  # 10 minutes
    task_max_retries=3,
    task_default_retry_delay=60,
    # Result backend settings
    result_expires=3600,  # 1 hour
    result_backend_transport_options={
        "master_name": "mymaster",
        "visibility_timeout": 3600,
    },
    # Beat schedule for periodic tasks - TEMPORARILY DISABLED FOR DEBUGGING
    beat_schedule={
        # All beat schedules temporarily disabled to isolate the day=1 error
        # Will re-enable after fixing the configuration issue
    },
)

# Task discovery
celery_app.autodiscover_tasks()


# Error handling
@celery_app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery setup."""
    print(f"Request: {self.request!r}")
    return "Celery is working!"


# Health check task
@celery_app.task
def health_check():
    """Health check task for monitoring."""
    import datetime

    return {
        "status": "healthy",
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "worker_id": celery_app.control.inspect().active(),
    }


if __name__ == "__main__":
    celery_app.start()

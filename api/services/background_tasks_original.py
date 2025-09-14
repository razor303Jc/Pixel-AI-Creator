"""
Background task processor for Pixel AI Creator.

Handles async conversation processing, analytics generation,
and system maintenance tasks.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from celery import current_task
from sqlalchemy.orm import Session

from core.celery_app import celery_app
from core.database import get_db
# from services.cache_service import RedisCache  # Temporarily disabled
# from services.analytics_service import AnalyticsService  # Temporarily disabled
# from models.conversation import Conversation  # Temporarily disabled
# from models.user import User  # Temporarily disabled
# from models.chatbot import Chatbot  # Temporarily disabled
from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class BackgroundTaskProcessor:
    """Handles background task processing and coordination."""

    def __init__(self):
        self.cache_service = RedisCache()
        self.analytics_service = AnalyticsService()

    async def process_conversation_async(
        self,
        conversation_id: str,
        user_message: str,
        bot_id: str,
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Process conversation asynchronously."""
        try:
            # Get database session
            db = next(get_db())

            # Retrieve conversation
            conversation = (
                db.query(Conversation)
                .filter(Conversation.id == conversation_id)
                .first()
            )

            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")

            # Process the conversation
            result = await self._process_conversation_internal(
                conversation, user_message, bot_id, metadata
            )

            # Cache the result
            cache_key = f"conversation:{conversation_id}:result"
            await self.cache_service.set(cache_key, result, ttl=3600)

            # Update conversation status
            conversation.status = "completed"
            conversation.updated_at = datetime.utcnow()
            db.commit()

            return result

        except Exception as e:
            logger.error(f"Error processing conversation {conversation_id}: {e}")
            raise
        finally:
            db.close()

    async def _process_conversation_internal(
        self,
        conversation: Conversation,
        user_message: str,
        bot_id: str,
        metadata: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Internal conversation processing logic."""
        # Simulate AI processing (replace with actual AI service call)
        await asyncio.sleep(0.1)  # Simulate processing time

        response = {
            "conversation_id": conversation.id,
            "response": f"Processed: {user_message}",
            "bot_id": bot_id,
            "processed_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }

        return response

    async def generate_analytics_report(
        self, report_type: str, date_range: Dict[str, datetime]
    ) -> Dict[str, Any]:
        """Generate analytics report for specified date range."""
        try:
            # Generate analytics
            analytics_data = await self.analytics_service.generate_report(
                report_type, date_range
            )

            # Cache the report
            cache_key = f"analytics:{report_type}:{date_range['start'].date()}"
            await self.cache_service.set(cache_key, analytics_data, ttl=7200)

            return analytics_data

        except Exception as e:
            logger.error(f"Error generating analytics report: {e}")
            raise

    async def cleanup_old_data(self, days_old: int = 30) -> Dict[str, int]:
        """Clean up old conversation data."""
        try:
            db = next(get_db())
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)

            # Count old conversations
            old_conversations = (
                db.query(Conversation)
                .filter(
                    Conversation.created_at < cutoff_date,
                    Conversation.status == "completed",
                )
                .count()
            )

            # Delete old conversations (in batches)
            batch_size = 100
            deleted_count = 0

            while True:
                batch = (
                    db.query(Conversation)
                    .filter(
                        Conversation.created_at < cutoff_date,
                        Conversation.status == "completed",
                    )
                    .limit(batch_size)
                    .all()
                )

                if not batch:
                    break

                for conversation in batch:
                    db.delete(conversation)
                    deleted_count += 1

                db.commit()
                await asyncio.sleep(0.1)  # Prevent overwhelming the DB

            # Clean up cache
            cache_cleaned = await self.cache_service.cleanup_expired()

            result = {
                "conversations_deleted": deleted_count,
                "cache_keys_cleaned": cache_cleaned,
                "cutoff_date": cutoff_date.isoformat(),
            }

            logger.info(f"Cleanup completed: {result}")
            return result

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            raise
        finally:
            db.close()


# Celery task definitions
@celery_app.task(bind=True, max_retries=3)
def process_conversation_task(
    self,
    conversation_id: str,
    user_message: str,
    bot_id: str,
    metadata: Optional[Dict] = None,
):
    """Celery task for processing conversations."""
    try:
        processor = BackgroundTaskProcessor()

        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        result = loop.run_until_complete(
            processor.process_conversation_async(
                conversation_id, user_message, bot_id, metadata
            )
        )

        return result

    except Exception as e:
        logger.error(f"Task failed for conversation {conversation_id}: {e}")
        raise self.retry(countdown=60, exc=e)


@celery_app.task(bind=True)
def generate_analytics_task(self, report_type: str, start_date: str, end_date: str):
    """Celery task for generating analytics reports."""
    try:
        processor = BackgroundTaskProcessor()

        date_range = {
            "start": datetime.fromisoformat(start_date),
            "end": datetime.fromisoformat(end_date),
        }

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        result = loop.run_until_complete(
            processor.generate_analytics_report(report_type, date_range)
        )

        return result

    except Exception as e:
        logger.error(f"Analytics task failed: {e}")
        raise


@celery_app.task
def cleanup_old_conversations():
    """Scheduled task to clean up old conversations."""
    try:
        processor = BackgroundTaskProcessor()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        result = loop.run_until_complete(processor.cleanup_old_data(days_old=30))

        return result

    except Exception as e:
        logger.error(f"Cleanup task failed: {e}")
        raise


@celery_app.task
def send_email_notification(
    recipient_email: str, subject: str, body: str, email_type: str = "text"
):
    """Send email notification."""
    try:
        msg = MIMEMultipart()
        msg["From"] = settings.SMTP_USER
        msg["To"] = recipient_email
        msg["Subject"] = subject

        if email_type == "html":
            msg.attach(MIMEText(body, "html"))
        else:
            msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)

        text = msg.as_string()
        server.sendmail(settings.SMTP_USER, recipient_email, text)
        server.quit()

        logger.info(f"Email sent successfully to {recipient_email}")
        return {"status": "sent", "recipient": recipient_email}

    except Exception as e:
        logger.error(f"Failed to send email to {recipient_email}: {e}")
        raise


@celery_app.task
def backup_database():
    """Create database backup."""
    try:
        import subprocess
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"/tmp/backup_{timestamp}.sql"

        # PostgreSQL backup command
        cmd = [
            "pg_dump",
            "-h",
            settings.DATABASE_HOST,
            "-U",
            settings.DATABASE_USER,
            "-d",
            settings.DATABASE_NAME,
            "-f",
            backup_file,
        ]

        # Set password via environment
        env = {"PGPASSWORD": settings.DATABASE_PASSWORD}

        result = subprocess.run(cmd, env=env, capture_output=True, text=True)

        if result.returncode == 0:
            logger.info(f"Database backup created: {backup_file}")
            return {"status": "success", "backup_file": backup_file}
        else:
            logger.error(f"Database backup failed: {result.stderr}")
            raise Exception(f"Backup failed: {result.stderr}")

    except Exception as e:
        logger.error(f"Database backup task failed: {e}")
        raise


@celery_app.task
def generate_system_health_report():
    """Generate system health report."""
    try:
        import psutil
        import redis

        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        # Redis health
        try:
            r = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                decode_responses=True,
            )
            redis_info = r.info()
            redis_healthy = True
        except Exception:
            redis_healthy = False
            redis_info = {}

        # Database health
        try:
            db = next(get_db())
            db.execute("SELECT 1")
            db_healthy = True
        except Exception:
            db_healthy = False
        finally:
            if "db" in locals():
                db.close()

        health_report = {
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "disk_percent": (disk.used / disk.total) * 100,
            },
            "services": {
                "redis_healthy": redis_healthy,
                "database_healthy": db_healthy,
            },
            "redis_info": (
                {
                    "connected_clients": redis_info.get("connected_clients", 0),
                    "used_memory_human": redis_info.get("used_memory_human", "0B"),
                }
                if redis_healthy
                else {}
            ),
        }

        # Cache the health report
        cache_service = RedisCache()
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        loop.run_until_complete(
            cache_service.set("system:health", health_report, ttl=900)
        )

        return health_report

    except Exception as e:
        logger.error(f"Health report generation failed: {e}")
        raise


# Task monitoring and management
class TaskManager:
    """Manages background task execution and monitoring."""

    @staticmethod
    def get_task_status(task_id: str) -> Dict[str, Any]:
        """Get status of a specific task."""
        result = celery_app.AsyncResult(task_id)
        return {
            "task_id": task_id,
            "status": result.status,
            "result": result.result,
            "info": result.info,
        }

    @staticmethod
    def cancel_task(task_id: str) -> bool:
        """Cancel a running task."""
        celery_app.control.revoke(task_id, terminate=True)
        return True

    @staticmethod
    def get_active_tasks() -> List[Dict[str, Any]]:
        """Get list of active tasks."""
        inspect = celery_app.control.inspect()
        active_tasks = inspect.active()

        if not active_tasks:
            return []

        all_tasks = []
        for worker, tasks in active_tasks.items():
            for task in tasks:
                all_tasks.append(
                    {
                        "worker": worker,
                        "task_id": task["id"],
                        "name": task["name"],
                        "args": task["args"],
                        "kwargs": task["kwargs"],
                    }
                )

        return all_tasks

"""
Conversation processor service for handling async conversation processing.

Manages conversation queuing, processing, and state management.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json

from celery import current_task
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from core.celery_app import celery_app
from core.database import get_db
from services.cache_service import CacheService
from services.ai_service import AIService
from models.conversation import Conversation
from models.message import Message
from models.user import User
from models.chatbot import Chatbot

logger = logging.getLogger(__name__)


class ConversationProcessor:
    """Handles conversation processing and management."""

    def __init__(self):
        self.cache_service = CacheService()
        self.ai_service = AIService()

    async def queue_conversation(
        self,
        conversation_id: str,
        user_message: str,
        bot_id: str,
        user_id: str,
        priority: str = "normal",
    ) -> str:
        """Queue a conversation for async processing."""
        try:
            # Create conversation processing task
            from services.background_tasks import process_conversation_task

            task = process_conversation_task.apply_async(
                args=[conversation_id, user_message, bot_id],
                kwargs={"metadata": {"user_id": user_id, "priority": priority}},
                queue="conversations",
            )

            # Cache task info
            task_info = {
                "task_id": task.id,
                "conversation_id": conversation_id,
                "status": "queued",
                "queued_at": datetime.utcnow().isoformat(),
                "priority": priority,
            }

            cache_key = f"conversation_task:{conversation_id}"
            await self.cache_service.set(cache_key, task_info, ttl=3600)

            return task.id

        except Exception as e:
            logger.error(f"Error queuing conversation {conversation_id}: {e}")
            raise

    async def get_conversation_status(self, conversation_id: str) -> Dict[str, Any]:
        """Get status of conversation processing."""
        try:
            cache_key = f"conversation_task:{conversation_id}"
            task_info = await self.cache_service.get(cache_key)

            if not task_info:
                return {"status": "not_found"}

            # Get Celery task result
            task_result = celery_app.AsyncResult(task_info["task_id"])

            status_info = {
                "conversation_id": conversation_id,
                "task_id": task_info["task_id"],
                "status": task_result.status.lower(),
                "queued_at": task_info["queued_at"],
                "priority": task_info.get("priority", "normal"),
            }

            if task_result.ready():
                if task_result.successful():
                    status_info["result"] = task_result.result
                    status_info["completed_at"] = datetime.utcnow().isoformat()
                else:
                    status_info["error"] = str(task_result.info)

            return status_info

        except Exception as e:
            logger.error(f"Error getting conversation status: {e}")
            return {"status": "error", "error": str(e)}

    async def process_pending_conversations(self) -> Dict[str, int]:
        """Process pending conversations in the queue."""
        try:
            db = next(get_db())

            # Get pending conversations
            pending_conversations = (
                db.query(Conversation)
                .filter(
                    and_(
                        Conversation.status == "pending",
                        Conversation.created_at
                        > datetime.utcnow() - timedelta(hours=24),
                    )
                )
                .limit(50)
                .all()
            )  # Process in batches

            processed_count = 0
            queued_count = 0

            for conversation in pending_conversations:
                try:
                    # Get the latest user message
                    latest_message = (
                        db.query(Message)
                        .filter(
                            and_(
                                Message.conversation_id == conversation.id,
                                Message.sender_type == "user",
                            )
                        )
                        .order_by(Message.created_at.desc())
                        .first()
                    )

                    if latest_message:
                        # Queue for processing
                        task_id = await self.queue_conversation(
                            conversation.id,
                            latest_message.content,
                            conversation.chatbot_id,
                            conversation.user_id,
                            priority="normal",
                        )

                        # Update conversation status
                        conversation.status = "processing"
                        conversation.updated_at = datetime.utcnow()

                        queued_count += 1

                    processed_count += 1

                except Exception as e:
                    logger.error(
                        f"Error processing conversation {conversation.id}: {e}"
                    )
                    continue

            db.commit()

            result = {
                "processed": processed_count,
                "queued": queued_count,
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Cache the processing stats
            await self.cache_service.set(
                "conversation_processing_stats", result, ttl=300
            )

            return result

        except Exception as e:
            logger.error(f"Error processing pending conversations: {e}")
            raise
        finally:
            db.close()

    async def cleanup_old_conversations(self, days_old: int = 7) -> Dict[str, int]:
        """Clean up old completed conversations."""
        try:
            db = next(get_db())
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)

            # Find old conversations to archive
            old_conversations = (
                db.query(Conversation)
                .filter(
                    and_(
                        Conversation.status.in_(["completed", "failed"]),
                        Conversation.updated_at < cutoff_date,
                    )
                )
                .all()
            )

            archived_count = 0
            deleted_count = 0

            for conversation in old_conversations:
                try:
                    # Archive important conversations, delete others
                    if (
                        conversation.importance_score
                        and conversation.importance_score > 7
                    ):
                        conversation.status = "archived"
                        archived_count += 1
                    else:
                        # Delete messages first
                        db.query(Message).filter(
                            Message.conversation_id == conversation.id
                        ).delete()

                        # Delete conversation
                        db.delete(conversation)
                        deleted_count += 1

                except Exception as e:
                    logger.error(f"Error cleaning conversation {conversation.id}: {e}")
                    continue

            db.commit()

            # Clean up conversation task cache
            cache_cleaned = await self._cleanup_conversation_cache(cutoff_date)

            result = {
                "conversations_archived": archived_count,
                "conversations_deleted": deleted_count,
                "cache_keys_cleaned": cache_cleaned,
                "cutoff_date": cutoff_date.isoformat(),
            }

            logger.info(f"Conversation cleanup completed: {result}")
            return result

        except Exception as e:
            logger.error(f"Error during conversation cleanup: {e}")
            raise
        finally:
            db.close()

    async def _cleanup_conversation_cache(self, cutoff_date: datetime) -> int:
        """Clean up old conversation cache entries."""
        try:
            # This would need to be implemented based on your cache backend
            # For now, we'll just return 0
            return 0

        except Exception as e:
            logger.error(f"Error cleaning conversation cache: {e}")
            return 0

    async def get_conversation_metrics(self) -> Dict[str, Any]:
        """Get conversation processing metrics."""
        try:
            db = next(get_db())

            # Get conversation counts by status
            total_conversations = db.query(Conversation).count()
            pending_conversations = (
                db.query(Conversation).filter(Conversation.status == "pending").count()
            )
            processing_conversations = (
                db.query(Conversation)
                .filter(Conversation.status == "processing")
                .count()
            )
            completed_conversations = (
                db.query(Conversation)
                .filter(Conversation.status == "completed")
                .count()
            )
            failed_conversations = (
                db.query(Conversation).filter(Conversation.status == "failed").count()
            )

            # Get processing stats from cache
            processing_stats = (
                await self.cache_service.get("conversation_processing_stats") or {}
            )

            # Calculate success rate
            total_processed = completed_conversations + failed_conversations
            success_rate = (
                (completed_conversations / total_processed * 100)
                if total_processed > 0
                else 0
            )

            metrics = {
                "total_conversations": total_conversations,
                "status_breakdown": {
                    "pending": pending_conversations,
                    "processing": processing_conversations,
                    "completed": completed_conversations,
                    "failed": failed_conversations,
                },
                "success_rate": round(success_rate, 2),
                "last_processing_stats": processing_stats,
                "timestamp": datetime.utcnow().isoformat(),
            }

            # Cache metrics
            await self.cache_service.set("conversation_metrics", metrics, ttl=300)

            return metrics

        except Exception as e:
            logger.error(f"Error getting conversation metrics: {e}")
            raise
        finally:
            db.close()


# Celery task definitions for conversation processing
@celery_app.task
def process_pending_conversations():
    """Scheduled task to process pending conversations."""
    try:
        processor = ConversationProcessor()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        result = loop.run_until_complete(processor.process_pending_conversations())

        return result

    except Exception as e:
        logger.error(f"Process pending conversations task failed: {e}")
        raise


@celery_app.task
def cleanup_old_conversations():
    """Scheduled task to clean up old conversations."""
    try:
        processor = ConversationProcessor()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        result = loop.run_until_complete(
            processor.cleanup_old_conversations(days_old=7)
        )

        return result

    except Exception as e:
        logger.error(f"Cleanup old conversations task failed: {e}")
        raise


@celery_app.task
def generate_conversation_metrics():
    """Task to generate conversation processing metrics."""
    try:
        processor = ConversationProcessor()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        metrics = loop.run_until_complete(processor.get_conversation_metrics())

        return metrics

    except Exception as e:
        logger.error(f"Generate conversation metrics task failed: {e}")
        raise


# High-priority conversation processor
class PriorityConversationProcessor(ConversationProcessor):
    """Handles high-priority conversation processing."""

    async def queue_priority_conversation(
        self, conversation_id: str, user_message: str, bot_id: str, user_id: str
    ) -> str:
        """Queue a high-priority conversation for immediate processing."""
        try:
            from services.background_tasks import process_conversation_task

            # Use high priority queue
            task = process_conversation_task.apply_async(
                args=[conversation_id, user_message, bot_id],
                kwargs={"metadata": {"user_id": user_id, "priority": "high"}},
                queue="conversations",
                priority=9,  # High priority
            )

            # Cache with shorter TTL for faster access
            task_info = {
                "task_id": task.id,
                "conversation_id": conversation_id,
                "status": "queued",
                "priority": "high",
                "queued_at": datetime.utcnow().isoformat(),
            }

            cache_key = f"priority_conversation_task:{conversation_id}"
            await self.cache_service.set(cache_key, task_info, ttl=1800)

            return task.id

        except Exception as e:
            logger.error(f"Error queuing priority conversation: {e}")
            raise


# Conversation batch processor
class BatchConversationProcessor:
    """Handles batch conversation processing."""

    def __init__(self):
        self.cache_service = CacheService()

    async def process_conversation_batch(
        self, conversation_batch: List[Dict[str, Any]], batch_id: str
    ) -> Dict[str, Any]:
        """Process a batch of conversations."""
        try:
            from services.background_tasks import process_conversation_task

            task_ids = []

            for conversation_data in conversation_batch:
                task = process_conversation_task.apply_async(
                    args=[
                        conversation_data["conversation_id"],
                        conversation_data["user_message"],
                        conversation_data["bot_id"],
                    ],
                    kwargs={
                        "metadata": {
                            "user_id": conversation_data["user_id"],
                            "batch_id": batch_id,
                            "priority": "batch",
                        }
                    },
                    queue="conversations",
                )
                task_ids.append(task.id)

            # Cache batch info
            batch_info = {
                "batch_id": batch_id,
                "task_ids": task_ids,
                "conversation_count": len(conversation_batch),
                "status": "processing",
                "created_at": datetime.utcnow().isoformat(),
            }

            cache_key = f"conversation_batch:{batch_id}"
            await self.cache_service.set(cache_key, batch_info, ttl=7200)

            return {
                "batch_id": batch_id,
                "queued_conversations": len(task_ids),
                "task_ids": task_ids,
            }

        except Exception as e:
            logger.error(f"Error processing conversation batch: {e}")
            raise

    async def get_batch_status(self, batch_id: str) -> Dict[str, Any]:
        """Get status of conversation batch processing."""
        try:
            cache_key = f"conversation_batch:{batch_id}"
            batch_info = await self.cache_service.get(cache_key)

            if not batch_info:
                return {"status": "not_found"}

            # Check status of all tasks in batch
            completed_tasks = 0
            failed_tasks = 0

            for task_id in batch_info["task_ids"]:
                task_result = celery_app.AsyncResult(task_id)
                if task_result.ready():
                    if task_result.successful():
                        completed_tasks += 1
                    else:
                        failed_tasks += 1

            total_tasks = len(batch_info["task_ids"])
            pending_tasks = total_tasks - completed_tasks - failed_tasks

            # Determine overall batch status
            if completed_tasks == total_tasks:
                batch_status = "completed"
            elif failed_tasks == total_tasks:
                batch_status = "failed"
            elif completed_tasks + failed_tasks == total_tasks:
                batch_status = "completed_with_errors"
            else:
                batch_status = "processing"

            return {
                "batch_id": batch_id,
                "status": batch_status,
                "total_conversations": total_tasks,
                "completed": completed_tasks,
                "failed": failed_tasks,
                "pending": pending_tasks,
                "progress_percent": round(
                    (completed_tasks + failed_tasks) / total_tasks * 100, 2
                ),
                "created_at": batch_info["created_at"],
            }

        except Exception as e:
            logger.error(f"Error getting batch status: {e}")
            return {"status": "error", "error": str(e)}

"""
Analytics processor service for generating performance and usage analytics.

Handles real-time analytics generation, reporting, and data aggregation.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import defaultdict
import json

from celery import current_task
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc

from core.celery_app import celery_app
from core.database import get_db
from services.cache_service import RedisCache
from models.database_schema import (
    Conversation,
    Message,
    User,
    Chatbot,
    ConversationAnalytics,
)

logger = logging.getLogger(__name__)


class AnalyticsProcessor:
    """Handles analytics generation and processing."""

    def __init__(self):
        self.cache_service = RedisCache()

    async def generate_daily_analytics(
        self, target_date: datetime = None
    ) -> Dict[str, Any]:
        """Generate daily analytics report."""
        try:
            if not target_date:
                target_date = datetime.utcnow().date()

            start_date = datetime.combine(target_date, datetime.min.time())
            end_date = start_date + timedelta(days=1)

            db = next(get_db())

            # Conversation analytics
            conversation_stats = await self._get_conversation_analytics(
                db, start_date, end_date
            )

            # User engagement analytics
            user_stats = await self._get_user_engagement_analytics(
                db, start_date, end_date
            )

            # Bot performance analytics
            bot_stats = await self._get_bot_performance_analytics(
                db, start_date, end_date
            )

            # System performance analytics
            system_stats = await self._get_system_performance_analytics(
                start_date, end_date
            )

            analytics_report = {
                "report_type": "daily",
                "date": target_date.isoformat(),
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
                "conversation_analytics": conversation_stats,
                "user_engagement": user_stats,
                "bot_performance": bot_stats,
                "system_performance": system_stats,
                "generated_at": datetime.utcnow().isoformat(),
            }

            # Store in database
            analytics_record = Analytics(
                report_type="daily",
                period_start=start_date,
                period_end=end_date,
                data=analytics_report,
                created_at=datetime.utcnow(),
            )
            db.add(analytics_record)
            db.commit()

            # Cache the report
            cache_key = f"analytics:daily:{target_date.isoformat()}"
            await self.cache_service.set(cache_key, analytics_report, ttl=86400)

            return analytics_report

        except Exception as e:
            logger.error(f"Error generating daily analytics: {e}")
            raise
        finally:
            db.close()

    async def generate_weekly_analytics(
        self, target_week: datetime = None
    ) -> Dict[str, Any]:
        """Generate weekly analytics report."""
        try:
            if not target_week:
                target_week = datetime.utcnow()

            # Get start of week (Monday)
            start_date = target_week - timedelta(days=target_week.weekday())
            start_date = datetime.combine(start_date.date(), datetime.min.time())
            end_date = start_date + timedelta(days=7)

            db = next(get_db())

            # Aggregate daily reports for the week
            daily_reports = []
            for i in range(7):
                day = start_date + timedelta(days=i)
                cache_key = f"analytics:daily:{day.date().isoformat()}"
                daily_report = await self.cache_service.get(cache_key)
                if daily_report:
                    daily_reports.append(daily_report)

            # Generate weekly aggregations
            weekly_stats = await self._aggregate_weekly_stats(daily_reports)

            # Get week-specific analytics
            conversation_trends = await self._get_conversation_trends(
                db, start_date, end_date
            )

            user_retention = await self._get_user_retention_analytics(
                db, start_date, end_date
            )

            analytics_report = {
                "report_type": "weekly",
                "week_start": start_date.date().isoformat(),
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
                "aggregated_stats": weekly_stats,
                "conversation_trends": conversation_trends,
                "user_retention": user_retention,
                "daily_reports_count": len(daily_reports),
                "generated_at": datetime.utcnow().isoformat(),
            }

            # Store in database
            analytics_record = Analytics(
                report_type="weekly",
                period_start=start_date,
                period_end=end_date,
                data=analytics_report,
                created_at=datetime.utcnow(),
            )
            db.add(analytics_record)
            db.commit()

            # Cache the report
            cache_key = f"analytics:weekly:{start_date.date().isoformat()}"
            await self.cache_service.set(cache_key, analytics_report, ttl=604800)

            return analytics_report

        except Exception as e:
            logger.error(f"Error generating weekly analytics: {e}")
            raise
        finally:
            db.close()

    async def generate_monthly_analytics(
        self, target_month: datetime = None
    ) -> Dict[str, Any]:
        """Generate monthly analytics report."""
        try:
            if not target_month:
                target_month = datetime.utcnow()

            # Get start and end of month
            start_date = target_month.replace(day=1)
            start_date = datetime.combine(start_date.date(), datetime.min.time())

            if start_date.month == 12:
                next_month = start_date.replace(year=start_date.year + 1, month=1)
            else:
                next_month = start_date.replace(month=start_date.month + 1)

            end_date = next_month

            db = next(get_db())

            # Get monthly overview
            monthly_overview = await self._get_monthly_overview(
                db, start_date, end_date
            )

            # Get growth metrics
            growth_metrics = await self._get_growth_metrics(db, start_date, end_date)

            # Get top performers
            top_performers = await self._get_top_performers(db, start_date, end_date)

            analytics_report = {
                "report_type": "monthly",
                "month": start_date.strftime("%Y-%m"),
                "period": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
                "monthly_overview": monthly_overview,
                "growth_metrics": growth_metrics,
                "top_performers": top_performers,
                "generated_at": datetime.utcnow().isoformat(),
            }

            # Store in database
            analytics_record = Analytics(
                report_type="monthly",
                period_start=start_date,
                period_end=end_date,
                data=analytics_report,
                created_at=datetime.utcnow(),
            )
            db.add(analytics_record)
            db.commit()

            # Cache the report
            cache_key = f"analytics:monthly:{start_date.strftime('%Y-%m')}"
            await self.cache_service.set(cache_key, analytics_report, ttl=2592000)

            return analytics_report

        except Exception as e:
            logger.error(f"Error generating monthly analytics: {e}")
            raise
        finally:
            db.close()

    async def _get_conversation_analytics(
        self, db: Session, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Get conversation analytics for date range."""
        # Total conversations
        total_conversations = (
            db.query(Conversation)
            .filter(
                and_(
                    Conversation.created_at >= start_date,
                    Conversation.created_at < end_date,
                )
            )
            .count()
        )

        # Conversations by status
        status_counts = (
            db.query(Conversation.status, func.count(Conversation.id).label("count"))
            .filter(
                and_(
                    Conversation.created_at >= start_date,
                    Conversation.created_at < end_date,
                )
            )
            .group_by(Conversation.status)
            .all()
        )

        # Average conversation length
        avg_length = (
            db.query(
                func.avg(func.coalesce(Conversation.message_count, 0)).label(
                    "avg_length"
                )
            )
            .filter(
                and_(
                    Conversation.created_at >= start_date,
                    Conversation.created_at < end_date,
                )
            )
            .scalar()
            or 0
        )

        return {
            "total_conversations": total_conversations,
            "status_breakdown": {status: count for status, count in status_counts},
            "average_conversation_length": round(float(avg_length), 2),
        }

    async def _get_user_engagement_analytics(
        self, db: Session, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Get user engagement analytics for date range."""
        # Active users
        active_users = (
            db.query(func.count(func.distinct(Conversation.user_id)))
            .filter(
                and_(
                    Conversation.created_at >= start_date,
                    Conversation.created_at < end_date,
                )
            )
            .scalar()
            or 0
        )

        # New users
        new_users = (
            db.query(func.count(User.id))
            .filter(and_(User.created_at >= start_date, User.created_at < end_date))
            .scalar()
            or 0
        )

        # Messages per user
        user_message_counts = (
            db.query(
                Conversation.user_id,
                func.sum(func.coalesce(Conversation.message_count, 0)).label(
                    "total_messages"
                ),
            )
            .filter(
                and_(
                    Conversation.created_at >= start_date,
                    Conversation.created_at < end_date,
                )
            )
            .group_by(Conversation.user_id)
            .all()
        )

        if user_message_counts:
            avg_messages_per_user = sum(
                count.total_messages for count in user_message_counts
            ) / len(user_message_counts)
        else:
            avg_messages_per_user = 0

        return {
            "active_users": active_users,
            "new_users": new_users,
            "average_messages_per_user": round(avg_messages_per_user, 2),
        }

    async def _get_bot_performance_analytics(
        self, db: Session, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Get bot performance analytics for date range."""
        # Bot usage statistics
        bot_usage = (
            db.query(
                Conversation.chatbot_id,
                func.count(Conversation.id).label("conversation_count"),
                func.avg(func.coalesce(Conversation.satisfaction_score, 0)).label(
                    "avg_satisfaction"
                ),
            )
            .filter(
                and_(
                    Conversation.created_at >= start_date,
                    Conversation.created_at < end_date,
                )
            )
            .group_by(Conversation.chatbot_id)
            .all()
        )

        bot_stats = []
        for usage in bot_usage:
            bot = db.query(Chatbot).filter(Chatbot.id == usage.chatbot_id).first()

            bot_stats.append(
                {
                    "bot_id": usage.chatbot_id,
                    "bot_name": bot.name if bot else "Unknown",
                    "conversation_count": usage.conversation_count,
                    "average_satisfaction": round(
                        float(usage.avg_satisfaction or 0), 2
                    ),
                }
            )

        return {"bot_statistics": bot_stats, "total_bots_used": len(bot_stats)}

    async def _get_system_performance_analytics(
        self, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Get system performance analytics for date range."""
        # Get system metrics from cache
        system_health_reports = []

        # Try to get health reports for the period
        current_date = start_date
        while current_date < end_date:
            health_report = await self.cache_service.get(
                f"system:health:{current_date.date().isoformat()}"
            )
            if health_report:
                system_health_reports.append(health_report)
            current_date += timedelta(hours=1)

        if system_health_reports:
            avg_cpu = sum(
                report.get("system", {}).get("cpu_percent", 0)
                for report in system_health_reports
            ) / len(system_health_reports)

            avg_memory = sum(
                report.get("system", {}).get("memory_percent", 0)
                for report in system_health_reports
            ) / len(system_health_reports)
        else:
            avg_cpu = 0
            avg_memory = 0

        return {
            "average_cpu_usage": round(avg_cpu, 2),
            "average_memory_usage": round(avg_memory, 2),
            "health_reports_count": len(system_health_reports),
        }

    async def _aggregate_weekly_stats(
        self, daily_reports: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Aggregate daily reports into weekly statistics."""
        if not daily_reports:
            return {}

        total_conversations = sum(
            report.get("conversation_analytics", {}).get("total_conversations", 0)
            for report in daily_reports
        )

        total_active_users = sum(
            report.get("user_engagement", {}).get("active_users", 0)
            for report in daily_reports
        )

        total_new_users = sum(
            report.get("user_engagement", {}).get("new_users", 0)
            for report in daily_reports
        )

        return {
            "total_conversations": total_conversations,
            "total_active_users": total_active_users,
            "total_new_users": total_new_users,
            "daily_average_conversations": round(
                total_conversations / len(daily_reports), 2
            ),
            "days_with_data": len(daily_reports),
        }

    async def _get_conversation_trends(
        self, db: Session, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Get conversation trends for the period."""
        # Daily conversation counts
        daily_counts = (
            db.query(
                func.date(Conversation.created_at).label("date"),
                func.count(Conversation.id).label("count"),
            )
            .filter(
                and_(
                    Conversation.created_at >= start_date,
                    Conversation.created_at < end_date,
                )
            )
            .group_by(func.date(Conversation.created_at))
            .all()
        )

        trend_data = [
            {"date": str(count.date), "conversations": count.count}
            for count in daily_counts
        ]

        return {
            "daily_trends": trend_data,
            "trend_direction": self._calculate_trend_direction(trend_data),
        }

    def _calculate_trend_direction(self, trend_data: List[Dict[str, Any]]) -> str:
        """Calculate trend direction from data points."""
        if len(trend_data) < 2:
            return "insufficient_data"

        first_half = trend_data[: len(trend_data) // 2]
        second_half = trend_data[len(trend_data) // 2 :]

        first_avg = sum(d["conversations"] for d in first_half) / len(first_half)
        second_avg = sum(d["conversations"] for d in second_half) / len(second_half)

        if second_avg > first_avg * 1.05:
            return "increasing"
        elif second_avg < first_avg * 0.95:
            return "decreasing"
        else:
            return "stable"

    async def _get_user_retention_analytics(
        self, db: Session, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Get user retention analytics."""
        # Users who had conversations in the period
        period_users = (
            db.query(func.distinct(Conversation.user_id))
            .filter(
                and_(
                    Conversation.created_at >= start_date,
                    Conversation.created_at < end_date,
                )
            )
            .subquery()
        )

        # Users who had conversations in previous period
        prev_start = start_date - (end_date - start_date)
        prev_users = (
            db.query(func.distinct(Conversation.user_id))
            .filter(
                and_(
                    Conversation.created_at >= prev_start,
                    Conversation.created_at < start_date,
                )
            )
            .subquery()
        )

        # Returning users
        returning_users = (
            db.query(func.count(period_users.c.user_id))
            .select_from(
                period_users.join(
                    prev_users, period_users.c.user_id == prev_users.c.user_id
                )
            )
            .scalar()
            or 0
        )

        total_period_users = (
            db.query(func.count(func.distinct(Conversation.user_id)))
            .filter(
                and_(
                    Conversation.created_at >= start_date,
                    Conversation.created_at < end_date,
                )
            )
            .scalar()
            or 0
        )

        retention_rate = (
            (returning_users / total_period_users * 100)
            if total_period_users > 0
            else 0
        )

        return {
            "total_users": total_period_users,
            "returning_users": returning_users,
            "retention_rate": round(retention_rate, 2),
        }

    async def _get_monthly_overview(
        self, db: Session, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Get monthly overview statistics."""
        # Get all conversations for the month
        monthly_conversations = (
            db.query(Conversation)
            .filter(
                and_(
                    Conversation.created_at >= start_date,
                    Conversation.created_at < end_date,
                )
            )
            .count()
        )

        # Get all users active in the month
        monthly_active_users = (
            db.query(func.count(func.distinct(Conversation.user_id)))
            .filter(
                and_(
                    Conversation.created_at >= start_date,
                    Conversation.created_at < end_date,
                )
            )
            .scalar()
            or 0
        )

        # Get new users registered in the month
        new_users = (
            db.query(User)
            .filter(and_(User.created_at >= start_date, User.created_at < end_date))
            .count()
        )

        return {
            "total_conversations": monthly_conversations,
            "active_users": monthly_active_users,
            "new_users": new_users,
            "conversations_per_user": round(
                (
                    monthly_conversations / monthly_active_users
                    if monthly_active_users > 0
                    else 0
                ),
                2,
            ),
        }

    async def _get_growth_metrics(
        self, db: Session, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Get growth metrics compared to previous period."""
        period_length = end_date - start_date
        prev_start = start_date - period_length
        prev_end = start_date

        # Current period metrics
        current_conversations = (
            db.query(Conversation)
            .filter(
                and_(
                    Conversation.created_at >= start_date,
                    Conversation.created_at < end_date,
                )
            )
            .count()
        )

        current_users = (
            db.query(func.count(func.distinct(Conversation.user_id)))
            .filter(
                and_(
                    Conversation.created_at >= start_date,
                    Conversation.created_at < end_date,
                )
            )
            .scalar()
            or 0
        )

        # Previous period metrics
        prev_conversations = (
            db.query(Conversation)
            .filter(
                and_(
                    Conversation.created_at >= prev_start,
                    Conversation.created_at < prev_end,
                )
            )
            .count()
        )

        prev_users = (
            db.query(func.count(func.distinct(Conversation.user_id)))
            .filter(
                and_(
                    Conversation.created_at >= prev_start,
                    Conversation.created_at < prev_end,
                )
            )
            .scalar()
            or 0
        )

        # Calculate growth rates
        conversation_growth = (
            ((current_conversations - prev_conversations) / prev_conversations * 100)
            if prev_conversations > 0
            else 0
        )

        user_growth = (
            ((current_users - prev_users) / prev_users * 100) if prev_users > 0 else 0
        )

        return {
            "conversation_growth_rate": round(conversation_growth, 2),
            "user_growth_rate": round(user_growth, 2),
            "current_period": {
                "conversations": current_conversations,
                "users": current_users,
            },
            "previous_period": {
                "conversations": prev_conversations,
                "users": prev_users,
            },
        }

    async def _get_top_performers(
        self, db: Session, start_date: datetime, end_date: datetime
    ) -> Dict[str, Any]:
        """Get top performing bots and users."""
        # Top bots by conversation count
        top_bots = (
            db.query(
                Conversation.chatbot_id,
                func.count(Conversation.id).label("conversation_count"),
                func.avg(func.coalesce(Conversation.satisfaction_score, 0)).label(
                    "avg_satisfaction"
                ),
            )
            .filter(
                and_(
                    Conversation.created_at >= start_date,
                    Conversation.created_at < end_date,
                )
            )
            .group_by(Conversation.chatbot_id)
            .order_by(desc("conversation_count"))
            .limit(5)
            .all()
        )

        top_bot_data = []
        for bot_stat in top_bots:
            bot = db.query(Chatbot).filter(Chatbot.id == bot_stat.chatbot_id).first()

            top_bot_data.append(
                {
                    "bot_id": bot_stat.chatbot_id,
                    "bot_name": bot.name if bot else "Unknown",
                    "conversation_count": bot_stat.conversation_count,
                    "average_satisfaction": round(
                        float(bot_stat.avg_satisfaction or 0), 2
                    ),
                }
            )

        # Most active users
        top_users = (
            db.query(
                Conversation.user_id,
                func.count(Conversation.id).label("conversation_count"),
            )
            .filter(
                and_(
                    Conversation.created_at >= start_date,
                    Conversation.created_at < end_date,
                )
            )
            .group_by(Conversation.user_id)
            .order_by(desc("conversation_count"))
            .limit(5)
            .all()
        )

        return {
            "top_bots": top_bot_data,
            "most_active_users": [
                {"user_id": user.user_id, "conversation_count": user.conversation_count}
                for user in top_users
            ],
        }


# Celery task definitions for analytics processing
@celery_app.task
def generate_daily_analytics():
    """Scheduled task to generate daily analytics."""
    try:
        processor = AnalyticsProcessor()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Generate for yesterday
        yesterday = datetime.utcnow().date() - timedelta(days=1)
        result = loop.run_until_complete(processor.generate_daily_analytics(yesterday))

        return result

    except Exception as e:
        logger.error(f"Generate daily analytics task failed: {e}")
        raise


@celery_app.task
def generate_weekly_analytics():
    """Scheduled task to generate weekly analytics."""
    try:
        processor = AnalyticsProcessor()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Generate for last week
        last_week = datetime.utcnow() - timedelta(days=7)
        result = loop.run_until_complete(processor.generate_weekly_analytics(last_week))

        return result

    except Exception as e:
        logger.error(f"Generate weekly analytics task failed: {e}")
        raise


@celery_app.task
def generate_monthly_analytics():
    """Scheduled task to generate monthly analytics."""
    try:
        processor = AnalyticsProcessor()

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Generate for last month
        last_month = datetime.utcnow() - timedelta(days=30)
        result = loop.run_until_complete(
            processor.generate_monthly_analytics(last_month)
        )

        return result

    except Exception as e:
        logger.error(f"Generate monthly analytics task failed: {e}")
        raise

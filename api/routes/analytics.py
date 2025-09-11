"""
Analytics API endpoints for conversation insights and performance metrics.

Provides REST API endpoints for accessing sentiment analysis,
topic modeling, and conversation performance data.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.database import get_db
from services.analytics_service_sync import AnalyticsService
from models.database_schema import Chatbot, Conversation

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/summary")
async def get_analytics_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get overall analytics summary for the platform.

    Returns conversation counts, message statistics, and sentiment distribution
    for the specified time period.
    """
    analytics_service = AdvancedAnalyticsService(db)
    return analytics_service.get_analytics_summary(days=days)


@router.get("/conversation/{conversation_id}/sentiment")
async def get_conversation_sentiment(
    conversation_id: int, db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get sentiment analysis for a specific conversation.

    Returns overall sentiment, sentiment timeline, and message-level
    sentiment scores for the conversation.
    """
    # Verify conversation exists
    conversation = (
        db.query(Conversation).filter(Conversation.id == conversation_id).first()
    )

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    analytics_service = AdvancedAnalyticsService(db)
    return analytics_service.analyze_conversation_sentiment(conversation_id)


@router.get("/bot/{bot_id}/performance")
async def get_bot_performance(
    bot_id: int,
    days: int = Query(30, ge=1, le=365, description="Number of days"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get performance metrics for a specific AI bot.

    Returns response times, satisfaction scores, engagement metrics,
    and topic distribution for the bot's conversations.
    """
    # Verify bot exists
    bot = db.query(Chatbot).filter(Chatbot.id == bot_id).first()

    if not bot:
        raise HTTPException(status_code=404, detail="Bot not found")

    analytics_service = AdvancedAnalyticsService(db)
    metrics = analytics_service.get_bot_performance_metrics(bot_id, days=days)

    return {
        "bot_id": bot_id,
        "bot_name": bot.name,
        "time_period_days": days,
        "metrics": {
            "total_messages": metrics.total_messages,
            "avg_response_time": metrics.avg_response_time,
            "resolution_rate": metrics.resolution_rate,
            "satisfaction_score": metrics.satisfaction_score,
            "engagement_score": metrics.engagement_score,
            "topic_distribution": metrics.topic_distribution,
        },
    }


@router.post("/message/sentiment")
async def analyze_message_sentiment(
    message_data: Dict[str, str], db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Analyze sentiment of a single message.

    Accepts a message text and returns sentiment analysis including
    score, magnitude, label, and confidence.
    """
    if "text" not in message_data:
        raise HTTPException(status_code=400, detail="Message text is required")

    message_text = message_data["text"]

    if not message_text.strip():
        raise HTTPException(status_code=400, detail="Message text cannot be empty")

    analytics_service = AdvancedAnalyticsService(db)
    sentiment = analytics_service.analyze_message_sentiment(message_text)

    return {
        "text": message_text,
        "sentiment": {
            "score": sentiment.score,
            "magnitude": sentiment.magnitude,
            "label": sentiment.label,
            "confidence": sentiment.confidence,
        },
    }


@router.get("/bots/leaderboard")
async def get_bot_leaderboard(
    days: int = Query(30, ge=1, le=365, description="Number of days"),
    metric: str = Query(
        "satisfaction_score",
        regex="^(satisfaction_score|engagement_score|avg_response_time)$",
        description="Metric to rank by",
    ),
    limit: int = Query(10, ge=1, le=50, description="Number of bots to return"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get leaderboard of bot performance metrics.

    Returns ranked list of bots based on the specified metric
    for the given time period.
    """
    # Get all bots
    bots = db.query(Chatbot).all()

    if not bots:
        return {"metric": metric, "time_period_days": days, "leaderboard": []}

    analytics_service = AdvancedAnalyticsService(db)
    bot_metrics = []

    for bot in bots:
        metrics = analytics_service.get_bot_performance_metrics(bot.id, days=days)

        # Skip bots with no activity
        if metrics.total_messages == 0:
            continue

        bot_metrics.append(
            {
                "bot_id": bot.id,
                "bot_name": bot.name,
                "satisfaction_score": metrics.satisfaction_score,
                "engagement_score": metrics.engagement_score,
                "avg_response_time": metrics.avg_response_time,
                "total_messages": metrics.total_messages,
                "resolution_rate": metrics.resolution_rate,
            }
        )

    # Sort by the specified metric
    # Lower response time is better
    reverse_sort = metric != "avg_response_time"
    bot_metrics.sort(key=lambda x: x[metric], reverse=reverse_sort)

    return {
        "metric": metric,
        "time_period_days": days,
        "leaderboard": bot_metrics[:limit],
    }


@router.get("/trends/sentiment")
async def get_sentiment_trends(
    days: int = Query(30, ge=1, le=365, description="Number of days"),
    granularity: str = Query(
        "daily", regex="^(daily|weekly)$", description="Time granularity for trends"
    ),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get sentiment trends over time.

    Returns sentiment distribution trends aggregated by day or week
    for the specified time period.
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Get conversations within the time period
    conversations = (
        db.query(Conversation)
        .filter(
            Conversation.created_at >= start_date, Conversation.created_at <= end_date
        )
        .all()
    )

    if not conversations:
        return {"time_period_days": days, "granularity": granularity, "trends": []}

    analytics_service = AdvancedAnalyticsService(db)

    # Group conversations by time period
    time_groups = {}

    for conv in conversations:
        if granularity == "daily":
            time_key = conv.created_at.date().isoformat()
        else:  # weekly
            # Get Monday of the week
            monday = conv.created_at.date() - timedelta(days=conv.created_at.weekday())
            time_key = monday.isoformat()

        if time_key not in time_groups:
            time_groups[time_key] = []
        time_groups[time_key].append(conv)

    # Analyze sentiment for each time period
    trends = []
    for time_key, convs in sorted(time_groups.items()):
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        total_score = 0

        for conv in convs:
            conv_sentiment = analytics_service.analyze_conversation_sentiment(conv.id)
            sentiment_counts[conv_sentiment["overall_sentiment"]] += 1
            total_score += conv_sentiment["sentiment_score"]

        avg_score = total_score / len(convs) if convs else 0

        trends.append(
            {
                "period": time_key,
                "conversation_count": len(convs),
                "avg_sentiment_score": avg_score,
                "sentiment_distribution": sentiment_counts,
            }
        )

    return {"time_period_days": days, "granularity": granularity, "trends": trends}


@router.get("/topics/distribution")
async def get_topic_distribution(
    days: int = Query(30, ge=1, le=365, description="Number of days"),
    bot_id: Optional[int] = Query(None, description="Filter by specific bot"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get topic distribution across conversations.

    Returns the distribution of conversation topics, optionally
    filtered by a specific bot.
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Build query
    query = db.query(Conversation).filter(
        Conversation.created_at >= start_date, Conversation.created_at <= end_date
    )

    if bot_id:
        # Verify bot exists
        bot = db.query(Chatbot).filter(Chatbot.id == bot_id).first()
        if not bot:
            raise HTTPException(status_code=404, detail="Bot not found")

        query = query.filter(Conversation.chatbot_id == bot_id)

    conversations = query.all()

    if not conversations:
        return {
            "time_period_days": days,
            "bot_id": bot_id,
            "topic_distribution": {},
            "total_conversations": 0,
        }

    analytics_service = AdvancedAnalyticsService(db)
    topic_distribution = analytics_service._extract_simple_topics(conversations)

    return {
        "time_period_days": days,
        "bot_id": bot_id,
        "topic_distribution": topic_distribution,
        "total_conversations": len(conversations),
    }


@router.get("/health")
async def get_analytics_health() -> Dict[str, Any]:
    """
    Get analytics service health status.

    Returns availability of analytics dependencies and service status.
    """
    from services.analytics_service import TEXTBLOB_AVAILABLE, OPENAI_AVAILABLE

    return {
        "status": "healthy",
        "dependencies": {
            "textblob_available": TEXTBLOB_AVAILABLE,
            "openai_available": OPENAI_AVAILABLE,
        },
        "features": {
            "sentiment_analysis": True,
            "topic_modeling": True,
            "performance_metrics": True,
            "trend_analysis": True,
        },
    }

"""
Analytics API routes for Pixel AI Creator.
Provides endpoints for conversation analytics, sentiment analysis,
and performance metrics.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any

from auth.middleware import get_current_user
from models.database_schema import User
from services.analytics_service_sync import AnalyticsService

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/summary")
async def get_analytics_summary(
    days: int = Query(7, ge=1, le=365), current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get overall analytics summary for the platform."""
    analytics_service = AnalyticsService()
    return analytics_service.get_analytics_summary(days=days)


@router.get("/conversation/{conversation_id}/sentiment")
async def get_conversation_sentiment(
    conversation_id: str, current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get sentiment analysis for a specific conversation."""
    try:
        analytics_service = AnalyticsService()
        return analytics_service.get_conversation_analytics(conversation_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/bot/{bot_id}/performance")
async def get_bot_performance(
    bot_id: str,
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get performance metrics for a specific chatbot."""
    try:
        analytics_service = AnalyticsService()
        return analytics_service.get_bot_performance(bot_id, days=days)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Performance analysis failed: {str(e)}"
        )


@router.get("/sentiment/trends")
async def get_sentiment_trends(
    days: int = Query(30, ge=1, le=365), current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get sentiment trends over time."""
    try:
        analytics_service = AnalyticsService()
        return analytics_service.get_sentiment_trends(days=days)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Trend analysis failed: {str(e)}")


@router.post("/message/sentiment")
async def analyze_message_sentiment(
    message: Dict[str, str], current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """Analyze sentiment of a single message."""
    if "text" not in message:
        raise HTTPException(status_code=400, detail="Message text is required")

    try:
        analytics_service = AnalyticsService()
        sentiment = analytics_service.analyze_message_sentiment(message["text"])

        return {
            "polarity": sentiment.polarity,
            "subjectivity": sentiment.subjectivity,
            "classification": sentiment.classification,
            "confidence": sentiment.confidence,
            "method": sentiment.method,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Sentiment analysis failed: {str(e)}"
        )


@router.get("/health")
async def analytics_health() -> Dict[str, str]:
    """Health check endpoint for analytics service."""
    return {"status": "healthy", "service": "analytics"}

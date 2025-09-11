"""
Simplified Analytics Service for immediate functionality.
Provides basic analytics without async complexity.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging
from collections import defaultdict

try:
    from textblob import TextBlob

    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class SentimentAnalysis:
    """Data class for sentiment analysis results."""

    polarity: float  # -1 (negative) to 1 (positive)
    subjectivity: float  # 0 (objective) to 1 (subjective)
    classification: str  # 'positive', 'negative', 'neutral'
    confidence: float  # 0 to 1
    method: str  # Analysis method used


@dataclass
class ConversationMetrics:
    """Data class for conversation analytics."""

    total_messages: int
    avg_response_time: float
    sentiment_distribution: Dict[str, int]
    topic_categories: List[str]
    engagement_score: float


@dataclass
class BotPerformance:
    """Data class for bot performance metrics."""

    bot_id: str
    bot_name: str
    total_conversations: int
    avg_sentiment_score: float
    response_accuracy: float
    user_satisfaction: float
    most_common_topics: List[str]


class AnalyticsService:
    """Simple analytics service with basic functionality."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def analyze_message_sentiment(self, message_text: str) -> SentimentAnalysis:
        """Analyze sentiment of a single message."""
        if not message_text:
            return SentimentAnalysis(
                polarity=0.0,
                subjectivity=0.0,
                classification="neutral",
                confidence=0.0,
                method="empty",
            )

        if TEXTBLOB_AVAILABLE:
            return self._textblob_sentiment(message_text)
        else:
            return self._simple_sentiment(message_text)

    def _textblob_sentiment(self, text: str) -> SentimentAnalysis:
        """Use TextBlob for sentiment analysis."""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity

            # Classify sentiment
            if polarity > 0.1:
                classification = "positive"
            elif polarity < -0.1:
                classification = "negative"
            else:
                classification = "neutral"

            # Calculate confidence based on absolute polarity
            confidence = min(abs(polarity) * 2, 1.0)

            return SentimentAnalysis(
                polarity=polarity,
                subjectivity=subjectivity,
                classification=classification,
                confidence=confidence,
                method="textblob",
            )
        except Exception as e:
            self.logger.error(f"TextBlob sentiment analysis failed: {e}")
            return self._simple_sentiment(text)

    def _simple_sentiment(self, text: str) -> SentimentAnalysis:
        """Simple keyword-based sentiment analysis."""
        positive_words = {
            "good",
            "great",
            "excellent",
            "amazing",
            "wonderful",
            "fantastic",
            "perfect",
            "love",
            "like",
            "awesome",
            "happy",
            "pleased",
            "satisfied",
            "thank",
            "thanks",
        }

        negative_words = {
            "bad",
            "terrible",
            "awful",
            "horrible",
            "hate",
            "dislike",
            "angry",
            "frustrated",
            "disappointed",
            "sad",
            "upset",
            "annoyed",
            "problem",
            "issue",
            "error",
        }

        words = text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)

        if positive_count > negative_count:
            polarity = 0.5
            classification = "positive"
        elif negative_count > positive_count:
            polarity = -0.5
            classification = "negative"
        else:
            polarity = 0.0
            classification = "neutral"

        confidence = (
            min((positive_count + negative_count) / len(words), 1.0) if words else 0.0
        )

        return SentimentAnalysis(
            polarity=polarity,
            subjectivity=0.5,  # Default moderate subjectivity
            classification=classification,
            confidence=confidence,
            method="keyword",
        )

    def get_analytics_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get overall analytics summary."""
        # For now, return mock data for immediate functionality
        return {
            "total_conversations": 150,
            "total_messages": 850,
            "sentiment_distribution": {"positive": 65, "negative": 20, "neutral": 65},
            "avg_response_time": 1.2,
            "top_topics": ["product questions", "support", "billing"],
            "period_days": days,
            "generated_at": datetime.utcnow().isoformat(),
        }

    def get_conversation_analytics(self, conversation_id: str) -> Dict[str, Any]:
        """Get analytics for a specific conversation."""
        # Mock data for immediate functionality
        return {
            "conversation_id": conversation_id,
            "total_messages": 12,
            "avg_sentiment": 0.3,
            "sentiment_trend": [0.2, 0.1, 0.4, 0.3, 0.5],
            "topics": ["product inquiry", "pricing"],
            "engagement_score": 0.75,
            "response_times": [1.1, 0.8, 1.5, 0.9, 1.2],
        }

    def get_bot_performance(self, bot_id: str, days: int = 30) -> Dict[str, Any]:
        """Get performance metrics for a specific bot."""
        # Mock data for immediate functionality
        return {
            "bot_id": bot_id,
            "period_days": days,
            "total_conversations": 45,
            "avg_sentiment_score": 0.25,
            "response_accuracy": 0.88,
            "user_satisfaction": 0.82,
            "common_topics": ["support", "billing", "features"],
            "performance_trend": [0.8, 0.85, 0.88, 0.87, 0.89],
        }

    def get_sentiment_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get sentiment trends over time."""
        # Mock data showing trend over time
        return {
            "period_days": days,
            "daily_sentiment": [
                {"date": "2024-01-01", "positive": 20, "negative": 5, "neutral": 15},
                {"date": "2024-01-02", "positive": 22, "negative": 3, "neutral": 18},
                {"date": "2024-01-03", "positive": 25, "negative": 4, "neutral": 16},
            ],
            "overall_trend": "improving",
            "trend_score": 0.15,  # Positive improvement
        }

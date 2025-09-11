"""
Advanced Analytics Service for conversation analysis and insights.

Provides sentiment analysis, topic modeling, and performance metrics
for chatbot conversations and user interactions.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Any
import logging
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, and_, select, text

try:
    from textblob import TextBlob

    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    logging.warning("TextBlob not available, falling back to basic sentiment analysis")

try:
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI not available, using local sentiment analysis only")

from models.database_schema import Conversation, Message


@dataclass
class SentimentAnalysis:
    """Data class for sentiment analysis results."""

    score: float  # -1 to 1, negative to positive
    magnitude: float  # 0 to 1, strength of sentiment
    label: str  # 'positive', 'negative', 'neutral'
    confidence: float  # 0 to 1, confidence in the prediction


@dataclass
class TopicAnalysis:
    """Data class for topic analysis results."""

    topics: List[str]
    keywords: List[str]
    categories: List[str]
    confidence: float


@dataclass
class ConversationMetrics:
    """Data class for conversation performance metrics."""

    total_messages: int
    avg_response_time: float
    resolution_rate: float
    satisfaction_score: float
    engagement_score: float
    topic_distribution: Dict[str, int]


class AdvancedAnalyticsService:
    """Advanced analytics service for conversation insights."""

    def __init__(self, db: AsyncSession):
        """Initialize the analytics service."""
        self.db = db
        self.logger = logging.getLogger(__name__)

        # Initialize sentiment keywords for fallback
        self.positive_keywords = {
            "good",
            "great",
            "excellent",
            "amazing",
            "wonderful",
            "fantastic",
            "awesome",
            "perfect",
            "love",
            "like",
            "happy",
            "satisfied",
            "pleased",
            "helpful",
            "thanks",
        }

        self.negative_keywords = {
            "bad",
            "terrible",
            "awful",
            "horrible",
            "hate",
            "dislike",
            "angry",
            "frustrated",
            "disappointed",
            "useless",
            "broken",
            "error",
            "problem",
            "issue",
        }

    def analyze_message_sentiment(self, message_text: str) -> SentimentAnalysis:
        """
        Analyze sentiment of a single message.

        Uses TextBlob if available, falls back to keyword-based analysis.
        """
        if TEXTBLOB_AVAILABLE:
            return self._textblob_sentiment(message_text)
        else:
            return self._keyword_sentiment(message_text)

    def _textblob_sentiment(self, text: str) -> SentimentAnalysis:
        """Analyze sentiment using TextBlob."""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity  # -1 to 1
        subjectivity = blob.sentiment.subjectivity  # 0 to 1

        # Determine label
        if polarity > 0.1:
            label = "positive"
        elif polarity < -0.1:
            label = "negative"
        else:
            label = "neutral"

        return SentimentAnalysis(
            score=polarity,
            magnitude=abs(polarity),
            label=label,
            confidence=1.0 - subjectivity,  # More objective = higher confidence
        )

    def _keyword_sentiment(self, text: str) -> SentimentAnalysis:
        """Fallback keyword-based sentiment analysis."""
        text_lower = text.lower()
        words = text_lower.split()

        positive_count = sum(1 for word in words if word in self.positive_keywords)
        negative_count = sum(1 for word in words if word in self.negative_keywords)

        total_sentiment_words = positive_count + negative_count

        if total_sentiment_words == 0:
            return SentimentAnalysis(
                score=0.0, magnitude=0.0, label="neutral", confidence=0.5
            )

        score = (positive_count - negative_count) / len(words)
        magnitude = total_sentiment_words / len(words)

        if score > 0.05:
            label = "positive"
        elif score < -0.05:
            label = "negative"
        else:
            label = "neutral"

        confidence = min(1.0, total_sentiment_words / max(1, len(words) * 0.1))

        return SentimentAnalysis(
            score=score, magnitude=magnitude, label=label, confidence=confidence
        )

    def analyze_conversation_sentiment(self, conversation_id: int) -> Dict[str, Any]:
        """Analyze sentiment for an entire conversation."""
        messages = (
            self.db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .all()
        )

        if not messages:
            return {
                "overall_sentiment": "neutral",
                "sentiment_score": 0.0,
                "message_count": 0,
                "sentiment_distribution": {"positive": 0, "negative": 0, "neutral": 0},
            }

        sentiments = []
        sentiment_counts = defaultdict(int)

        for message in messages:
            sentiment = self.analyze_message_sentiment(message.content)
            sentiments.append(sentiment)
            sentiment_counts[sentiment.label] += 1

        # Calculate overall sentiment
        avg_score = sum(s.score for s in sentiments) / len(sentiments)

        if avg_score > 0.1:
            overall_sentiment = "positive"
        elif avg_score < -0.1:
            overall_sentiment = "negative"
        else:
            overall_sentiment = "neutral"

        return {
            "overall_sentiment": overall_sentiment,
            "sentiment_score": avg_score,
            "message_count": len(messages),
            "sentiment_distribution": dict(sentiment_counts),
            "sentiment_timeline": [
                {
                    "message_id": msg.id,
                    "timestamp": msg.created_at.isoformat(),
                    "sentiment": sentiment.label,
                    "score": sentiment.score,
                }
                for msg, sentiment in zip(messages, sentiments)
            ],
        }

    def get_bot_performance_metrics(
        self, bot_id: int, days: int = 30
    ) -> ConversationMetrics:
        """Get performance metrics for a specific bot."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Get conversations for this bot in the time period
        conversations = (
            self.db.query(Conversation)
            .filter(
                and_(
                    Conversation.chatbot_id == bot_id,
                    Conversation.created_at >= start_date,
                    Conversation.created_at <= end_date,
                )
            )
            .all()
        )

        if not conversations:
            return ConversationMetrics(
                total_messages=0,
                avg_response_time=0.0,
                resolution_rate=0.0,
                satisfaction_score=0.0,
                engagement_score=0.0,
                topic_distribution={},
            )

        # Calculate metrics
        total_messages = sum(len(conv.messages) for conv in conversations)

        # Calculate average response time (simplified)
        response_times = []
        for conv in conversations:
            messages = sorted(conv.messages, key=lambda m: m.created_at)
            for i in range(1, len(messages)):
                if messages[i].is_from_user != messages[i - 1].is_from_user:
                    time_diff = (
                        messages[i].created_at - messages[i - 1].created_at
                    ).total_seconds()
                    response_times.append(time_diff)

        avg_response_time = (
            sum(response_times) / len(response_times) if response_times else 0.0
        )

        # Calculate sentiment-based satisfaction
        sentiment_scores = []
        for conv in conversations:
            conv_sentiment = self.analyze_conversation_sentiment(conv.id)
            sentiment_scores.append(conv_sentiment["sentiment_score"])

        satisfaction_score = (
            sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0
        )

        # Calculate engagement score (messages per conversation)
        engagement_score = total_messages / len(conversations)

        # Simple topic distribution (would be enhanced with proper NLP)
        topic_distribution = self._extract_simple_topics(conversations)

        return ConversationMetrics(
            total_messages=total_messages,
            avg_response_time=avg_response_time,
            # Placeholder - would need resolution tracking
            resolution_rate=0.8,
            satisfaction_score=satisfaction_score,
            engagement_score=engagement_score,
            topic_distribution=topic_distribution,
        )

    def _extract_simple_topics(
        self, conversations: List[Conversation]
    ) -> Dict[str, int]:
        """Extract simple topics from conversations using keyword analysis."""
        topics = defaultdict(int)

        # Define topic keywords
        topic_keywords = {
            "support": ["help", "problem", "issue", "error", "bug"],
            "sales": ["buy", "purchase", "price", "cost", "payment"],
            "information": ["what", "how", "when", "where", "why"],
            "feedback": ["feedback", "review", "opinion", "suggestion"],
            "general": ["hello", "hi", "thanks", "bye", "goodbye"],
        }

        for conv in conversations:
            for message in conv.messages:
                content_lower = message.content.lower()
                message_topics = set()

                for topic, keywords in topic_keywords.items():
                    if any(keyword in content_lower for keyword in keywords):
                        message_topics.add(topic)

                if not message_topics:
                    message_topics.add("other")

                for topic in message_topics:
                    topics[topic] += 1

        return dict(topics)

    def get_analytics_summary(self, days: int = 30) -> Dict[str, Any]:
        """Get overall analytics summary for the platform."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        # Get total conversations and messages
        total_conversations = (
            self.db.query(func.count(Conversation.id))
            .filter(Conversation.created_at >= start_date)
            .scalar()
        )

        total_messages = (
            self.db.query(func.count(Message.id))
            .join(Conversation)
            .filter(Conversation.created_at >= start_date)
            .scalar()
        )

        # Get sentiment distribution across all conversations
        recent_conversations = (
            self.db.query(Conversation)
            .filter(Conversation.created_at >= start_date)
            .limit(100)
            .all()
        )  # Sample for performance

        sentiment_summary = {"positive": 0, "negative": 0, "neutral": 0}

        for conv in recent_conversations:
            conv_sentiment = self.analyze_conversation_sentiment(conv.id)
            sentiment_summary[conv_sentiment["overall_sentiment"]] += 1

        return {
            "time_period_days": days,
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "avg_messages_per_conversation": (
                total_messages / max(1, total_conversations)
            ),
            "sentiment_distribution": sentiment_summary,
            "analyzed_conversations": len(recent_conversations),
        }

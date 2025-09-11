"""
Advanced Analytics Service for conversation analysis and insights.

Provides sentiment analysis, topic modeling, and performance metrics
for chatbot conversations and user interactions.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import logging
from collections import defaultdict

from sqlalchemy.orm import Session
from sqlalchemy import func, and_

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    logging.warning(
        "TextBlob not available, falling back to basic sentiment analysis"
    )

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning(
        "OpenAI not available, using local sentiment analysis only"
    )

from models.conversation import Conversation
from models.message import Message

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import logging
from collections import Counter, defaultdict
import json

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    logging.warning("TextBlob not available, falling back to basic sentiment analysis")

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI not available, using local sentiment analysis only")

from models.conversation import Conversation
from models.message import Message
from models.ai_bot import AIBot
from core.config import get_settings

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json

# External analytics libraries
from textblob import TextBlob
import openai
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from core.database import (
    Conversation, Message, ConversationAnalytics, 
    ChatbotProject, Client
)
from core.config import Settings

logger = logging.getLogger(__name__)
settings = Settings()


class SentimentType(Enum):
    """Sentiment classification types"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    MIXED = "mixed"


class TopicCategory(Enum):
    """Common conversation topic categories"""
    SUPPORT = "customer_support"
    SALES = "sales_inquiry"
    TECHNICAL = "technical_issue"
    BILLING = "billing_question"
    GENERAL = "general_inquiry"
    COMPLAINT = "complaint"
    COMPLIMENT = "compliment"
    FEATURE_REQUEST = "feature_request"


@dataclass
class SentimentAnalysis:
    """Sentiment analysis result"""
    sentiment: SentimentType
    confidence: float
    polarity: float  # -1 to 1
    subjectivity: float  # 0 to 1
    keywords: List[str]


@dataclass
class TopicAnalysis:
    """Topic modeling result"""
    primary_topic: TopicCategory
    confidence: float
    keywords: List[str]
    intent: str
    urgency_score: float  # 0 to 1


@dataclass
class ConversationMetrics:
    """Comprehensive conversation metrics"""
    conversation_id: str
    duration_minutes: float
    message_count: int
    avg_response_time: float
    sentiment_analysis: SentimentAnalysis
    topic_analysis: TopicAnalysis
    satisfaction_score: Optional[float]
    resolution_status: str
    escalation_needed: bool


class AdvancedAnalyticsService:
    """Advanced analytics service for conversation analysis"""
    
    def __init__(self):
        self.openai_client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
        
    async def analyze_message_sentiment(self, message_text: str) -> SentimentAnalysis:
        """
        Analyze sentiment of a single message using TextBlob and OpenAI
        """
        try:
            # Basic sentiment with TextBlob
            blob = TextBlob(message_text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Classify sentiment
            if polarity > 0.1:
                sentiment = SentimentType.POSITIVE
            elif polarity < -0.1:
                sentiment = SentimentType.NEGATIVE
            else:
                sentiment = SentimentType.NEUTRAL
                
            confidence = abs(polarity)
            
            # Extract keywords
            keywords = [word.lower() for word in blob.noun_phrases[:5]]
            
            # Enhanced analysis with OpenAI for complex cases
            if subjectivity > 0.7 or len(message_text) > 200:
                enhanced_sentiment = await self._enhanced_sentiment_analysis(message_text)
                if enhanced_sentiment:
                    sentiment = enhanced_sentiment.get('sentiment', sentiment)
                    confidence = max(confidence, enhanced_sentiment.get('confidence', confidence))
            
            return SentimentAnalysis(
                sentiment=sentiment,
                confidence=min(confidence, 1.0),
                polarity=polarity,
                subjectivity=subjectivity,
                keywords=keywords
            )
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return SentimentAnalysis(
                sentiment=SentimentType.NEUTRAL,
                confidence=0.5,
                polarity=0.0,
                subjectivity=0.5,
                keywords=[]
            )
    
    async def _enhanced_sentiment_analysis(self, text: str) -> Optional[Dict[str, Any]]:
        """Enhanced sentiment analysis using OpenAI for complex cases"""
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """Analyze the sentiment of the given text. Return a JSON with:
                        - sentiment: positive/negative/neutral/mixed
                        - confidence: 0.0-1.0
                        - reasoning: brief explanation
                        Focus on customer service context."""
                    },
                    {"role": "user", "content": text}
                ],
                max_tokens=150,
                temperature=0.1
            )
            
            result = response.choices[0].message.content
            return json.loads(result)
            
        except Exception as e:
            logger.warning(f"Enhanced sentiment analysis failed: {e}")
            return None
    
    async def analyze_conversation_topics(self, messages: List[str]) -> TopicAnalysis:
        """
        Analyze conversation topics and intent using AI
        """
        try:
            conversation_text = " ".join(messages[:10])  # Analyze first 10 messages
            
            # Use OpenAI for topic analysis
            response = await self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": """Analyze this customer service conversation and return JSON with:
                        - primary_topic: one of [customer_support, sales_inquiry, technical_issue, billing_question, general_inquiry, complaint, compliment, feature_request]
                        - confidence: 0.0-1.0
                        - keywords: list of 3-5 key terms
                        - intent: brief description of customer intent
                        - urgency_score: 0.0-1.0 based on urgency indicators"""
                    },
                    {"role": "user", "content": conversation_text}
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return TopicAnalysis(
                primary_topic=TopicCategory(result.get('primary_topic', 'general_inquiry')),
                confidence=result.get('confidence', 0.7),
                keywords=result.get('keywords', []),
                intent=result.get('intent', 'General inquiry'),
                urgency_score=result.get('urgency_score', 0.5)
            )
            
        except Exception as e:
            logger.error(f"Topic analysis failed: {e}")
            return TopicAnalysis(
                primary_topic=TopicCategory.GENERAL,
                confidence=0.5,
                keywords=[],
                intent="Unable to determine",
                urgency_score=0.5
            )
    
    async def analyze_conversation_metrics(
        self, 
        db: AsyncSession, 
        conversation_id: str
    ) -> ConversationMetrics:
        """
        Comprehensive conversation analysis with all metrics
        """
        try:
            # Get conversation with messages
            stmt = select(Conversation).options(
                selectinload(Conversation.messages)
            ).where(Conversation.id == conversation_id)
            
            result = await db.execute(stmt)
            conversation = result.scalar_one_or_none()
            
            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")
            
            messages = conversation.messages
            message_texts = [msg.content for msg in messages]
            
            # Calculate basic metrics
            duration = self._calculate_duration(messages)
            message_count = len(messages)
            avg_response_time = self._calculate_avg_response_time(messages)
            
            # Sentiment analysis on last 5 user messages
            user_messages = [msg.content for msg in messages if msg.role == 'user'][-5:]
            if user_messages:
                sentiment = await self.analyze_message_sentiment(" ".join(user_messages))
            else:
                sentiment = SentimentAnalysis(
                    sentiment=SentimentType.NEUTRAL,
                    confidence=0.5,
                    polarity=0.0,
                    subjectivity=0.5,
                    keywords=[]
                )
            
            # Topic analysis
            topic_analysis = await self.analyze_conversation_topics(message_texts)
            
            # Determine resolution status and escalation need
            resolution_status = self._determine_resolution_status(conversation, topic_analysis)
            escalation_needed = self._needs_escalation(sentiment, topic_analysis)
            
            return ConversationMetrics(
                conversation_id=conversation_id,
                duration_minutes=duration,
                message_count=message_count,
                avg_response_time=avg_response_time,
                sentiment_analysis=sentiment,
                topic_analysis=topic_analysis,
                satisfaction_score=self._calculate_satisfaction_score(sentiment, topic_analysis),
                resolution_status=resolution_status,
                escalation_needed=escalation_needed
            )
            
        except Exception as e:
            logger.error(f"Conversation metrics analysis failed: {e}")
            raise
    
    def _calculate_duration(self, messages: List[Message]) -> float:
        """Calculate conversation duration in minutes"""
        if len(messages) < 2:
            return 0.0
        
        start_time = min(msg.created_at for msg in messages)
        end_time = max(msg.created_at for msg in messages)
        duration = (end_time - start_time).total_seconds() / 60
        return round(duration, 2)
    
    def _calculate_avg_response_time(self, messages: List[Message]) -> float:
        """Calculate average response time between user and assistant messages"""
        response_times = []
        
        for i in range(len(messages) - 1):
            current_msg = messages[i]
            next_msg = messages[i + 1]
            
            if current_msg.role == 'user' and next_msg.role == 'assistant':
                response_time = (next_msg.created_at - current_msg.created_at).total_seconds()
                response_times.append(response_time)
        
        return round(sum(response_times) / len(response_times), 2) if response_times else 0.0
    
    def _determine_resolution_status(
        self, 
        conversation: Conversation, 
        topic_analysis: TopicAnalysis
    ) -> str:
        """Determine if conversation was resolved"""
        if conversation.status == 'completed':
            return 'resolved'
        elif topic_analysis.urgency_score > 0.8:
            return 'urgent_pending'
        elif conversation.status == 'active':
            return 'in_progress'
        else:
            return 'pending'
    
    def _needs_escalation(
        self, 
        sentiment: SentimentAnalysis, 
        topic_analysis: TopicAnalysis
    ) -> bool:
        """Determine if conversation needs human escalation"""
        escalation_triggers = [
            sentiment.sentiment == SentimentType.NEGATIVE and sentiment.confidence > 0.7,
            topic_analysis.primary_topic == TopicCategory.COMPLAINT,
            topic_analysis.urgency_score > 0.8,
            'refund' in topic_analysis.keywords,
            'cancel' in topic_analysis.keywords
        ]
        
        return any(escalation_triggers)
    
    def _calculate_satisfaction_score(
        self, 
        sentiment: SentimentAnalysis, 
        topic_analysis: TopicAnalysis
    ) -> float:
        """Calculate estimated customer satisfaction score"""
        base_score = 3.0  # Neutral baseline
        
        # Sentiment impact
        if sentiment.sentiment == SentimentType.POSITIVE:
            base_score += 1.5 * sentiment.confidence
        elif sentiment.sentiment == SentimentType.NEGATIVE:
            base_score -= 1.5 * sentiment.confidence
        
        # Topic impact
        if topic_analysis.primary_topic == TopicCategory.COMPLIMENT:
            base_score += 1.0
        elif topic_analysis.primary_topic == TopicCategory.COMPLAINT:
            base_score -= 1.0
        
        # Urgency impact
        if topic_analysis.urgency_score > 0.7:
            base_score -= 0.5
        
        return max(1.0, min(5.0, round(base_score, 1)))
    
    async def get_analytics_dashboard_data(
        self, 
        db: AsyncSession,
        chatbot_id: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get comprehensive analytics data for dashboard
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Base query
            query = select(Conversation).where(
                and_(
                    Conversation.created_at >= start_date,
                    Conversation.created_at <= end_date
                )
            )
            
            if chatbot_id:
                query = query.where(Conversation.chatbot_id == chatbot_id)
            
            conversations = await db.execute(query)
            conversations = conversations.scalars().all()
            
            # Analyze all conversations
            analytics_data = {
                'total_conversations': len(conversations),
                'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 0},
                'topic_distribution': {},
                'avg_satisfaction_score': 0.0,
                'escalation_rate': 0.0,
                'avg_response_time': 0.0,
                'resolution_rate': 0.0
            }
            
            total_satisfaction = 0
            escalations = 0
            total_response_time = 0
            resolved_count = 0
            
            for conv in conversations:
                try:
                    metrics = await self.analyze_conversation_metrics(db, conv.id)
                    
                    # Update sentiment distribution
                    sentiment_key = metrics.sentiment_analysis.sentiment.value
                    analytics_data['sentiment_distribution'][sentiment_key] += 1
                    
                    # Update topic distribution
                    topic_key = metrics.topic_analysis.primary_topic.value
                    analytics_data['topic_distribution'][topic_key] = \
                        analytics_data['topic_distribution'].get(topic_key, 0) + 1
                    
                    # Aggregate metrics
                    if metrics.satisfaction_score:
                        total_satisfaction += metrics.satisfaction_score
                    
                    if metrics.escalation_needed:
                        escalations += 1
                    
                    total_response_time += metrics.avg_response_time
                    
                    if metrics.resolution_status == 'resolved':
                        resolved_count += 1
                        
                except Exception as e:
                    logger.warning(f"Failed to analyze conversation {conv.id}: {e}")
                    continue
            
            # Calculate averages
            if conversations:
                analytics_data['avg_satisfaction_score'] = round(
                    total_satisfaction / len(conversations), 2
                )
                analytics_data['escalation_rate'] = round(
                    (escalations / len(conversations)) * 100, 1
                )
                analytics_data['avg_response_time'] = round(
                    total_response_time / len(conversations), 2
                )
                analytics_data['resolution_rate'] = round(
                    (resolved_count / len(conversations)) * 100, 1
                )
            
            return analytics_data
            
        except Exception as e:
            logger.error(f"Dashboard analytics failed: {e}")
            raise
    
    async def generate_performance_recommendations(
        self, 
        db: AsyncSession,
        chatbot_id: str
    ) -> List[Dict[str, str]]:
        """
        Generate AI-powered performance optimization recommendations
        """
        try:
            analytics_data = await self.get_analytics_dashboard_data(
                db, chatbot_id=chatbot_id, days=30
            )
            
            recommendations = []
            
            # Sentiment-based recommendations
            negative_rate = analytics_data['sentiment_distribution'].get('negative', 0)
            total_convs = analytics_data['total_conversations']
            
            if total_convs > 0 and (negative_rate / total_convs) > 0.3:
                recommendations.append({
                    'type': 'sentiment_improvement',
                    'priority': 'high',
                    'title': 'High Negative Sentiment Detected',
                    'description': f'{negative_rate} out of {total_convs} conversations show negative sentiment',
                    'action': 'Review conversation templates and add empathy training'
                })
            
            # Response time recommendations
            if analytics_data['avg_response_time'] > 30:
                recommendations.append({
                    'type': 'response_time',
                    'priority': 'medium',
                    'title': 'Slow Response Times',
                    'description': f'Average response time is {analytics_data["avg_response_time"]} seconds',
                    'action': 'Optimize chatbot processing or add quick response templates'
                })
            
            # Resolution rate recommendations
            if analytics_data['resolution_rate'] < 70:
                recommendations.append({
                    'type': 'resolution_rate',
                    'priority': 'high',
                    'title': 'Low Resolution Rate',
                    'description': f'Only {analytics_data["resolution_rate"]}% of conversations are resolved',
                    'action': 'Improve knowledge base and add escalation triggers'
                })
            
            # Escalation rate recommendations
            if analytics_data['escalation_rate'] > 20:
                recommendations.append({
                    'type': 'escalation_rate',
                    'priority': 'medium',
                    'title': 'High Escalation Rate',
                    'description': f'{analytics_data["escalation_rate"]}% of conversations need escalation',
                    'action': 'Enhance chatbot capabilities for common escalation triggers'
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Performance recommendations failed: {e}")
            return []

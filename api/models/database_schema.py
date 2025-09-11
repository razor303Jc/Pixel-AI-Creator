"""
Complete Database Schema with SQLAlchemy Models

This module provides the complete database schema for the Pixel-AI-Creator
application including all tables, relationships, and constraints.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    Text,
    JSON,
    ForeignKey,
    Index,
    UniqueConstraint,
    CheckConstraint,
    Float,
    Enum as SQLEnum,
)
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from enum import Enum

Base = declarative_base()


# Enums
class UserRole(str, Enum):
    """User role enumeration"""

    ADMIN = "admin"
    CLIENT = "client"
    USER = "user"


class ChatbotType(str, Enum):
    """Chatbot type enumeration"""

    CHATBOT = "chatbot"
    VOICE_ASSISTANT = "voice_assistant"
    AUTOMATION_BOT = "automation_bot"


class ChatbotComplexity(str, Enum):
    """Chatbot complexity enumeration"""

    BASIC = "basic"
    ADVANCED = "advanced"
    ENTERPRISE = "enterprise"


class ChatbotStatus(str, Enum):
    """Chatbot status enumeration"""

    PENDING = "pending"
    ANALYZING = "analyzing"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"
    DEPLOYED = "deployed"
    ARCHIVED = "archived"


class ConversationStatus(str, Enum):
    """Conversation status enumeration"""

    ACTIVE = "active"
    ARCHIVED = "archived"
    CLOSED = "closed"


class MessageRole(str, Enum):
    """Message role enumeration"""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


# === CORE MODELS ===


class User(Base):
    """User model for authentication and user management"""

    __tablename__ = "users"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Authentication
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    # Profile information
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    company_name = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)

    # User role and status
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)

    # API keys and settings
    openai_api_key = Column(String(255), nullable=True)
    preferred_language = Column(String(10), default="en", nullable=False)
    timezone = Column(String(50), default="UTC", nullable=False)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    last_login = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    clients = relationship(
        "Client", back_populates="user", cascade="all, delete-orphan"
    )
    chatbots = relationship(
        "Chatbot", back_populates="user", cascade="all, delete-orphan"
    )
    conversations = relationship(
        "Conversation", back_populates="user", cascade="all, delete-orphan"
    )

    # Indexes
    __table_args__ = (
        Index("idx_user_email", "email"),
        Index("idx_user_role", "role"),
        Index("idx_user_active", "is_active"),
        Index("idx_user_created", "created_at"),
    )

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"


class Client(Base):
    """Client model for customer management"""

    __tablename__ = "clients"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Client information
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, index=True)
    company = Column(String(255), nullable=True)
    website = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    industry = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)

    # Social media handles
    twitter_handle = Column(String(100), nullable=True)
    instagram_handle = Column(String(100), nullable=True)
    linkedin_profile = Column(String(255), nullable=True)

    # Status and settings
    status = Column(String(20), default="active", nullable=False)
    priority_level = Column(
        String(20), default="standard", nullable=False
    )  # low, standard, high, vip
    billing_email = Column(String(255), nullable=True)

    # Business metrics
    monthly_budget = Column(Float, nullable=True)
    project_count = Column(Integer, default=0, nullable=False)
    total_spent = Column(Float, default=0.0, nullable=False)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    last_contact = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="clients")
    chatbots = relationship(
        "Chatbot", back_populates="client", cascade="all, delete-orphan"
    )

    # Constraints and indexes
    __table_args__ = (
        Index("idx_client_email", "email"),
        Index("idx_client_status", "status"),
        Index("idx_client_user", "user_id"),
        Index("idx_client_industry", "industry"),
        Index("idx_client_created", "created_at"),
        CheckConstraint("monthly_budget >= 0", name="check_monthly_budget_positive"),
        CheckConstraint("total_spent >= 0", name="check_total_spent_positive"),
        CheckConstraint("project_count >= 0", name="check_project_count_positive"),
    )

    def __repr__(self):
        return f"<Client(id={self.id}, name='{self.name}', company='{self.company}')>"


class Chatbot(Base):
    """Chatbot project model"""

    __tablename__ = "chatbots"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Project information
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    project_type = Column(
        SQLEnum(ChatbotType), default=ChatbotType.CHATBOT, nullable=False
    )
    complexity = Column(
        SQLEnum(ChatbotComplexity), default=ChatbotComplexity.BASIC, nullable=False
    )

    # Status and progress
    status = Column(
        SQLEnum(ChatbotStatus), default=ChatbotStatus.PENDING, nullable=False
    )
    progress_percentage = Column(Integer, default=0, nullable=False)

    # Configuration
    personality_type = Column(String(50), default="customer_support", nullable=False)
    system_prompt = Column(Text, nullable=True)
    configuration = Column(JSON, nullable=True)  # Flexible configuration storage

    # AI and integration settings
    openai_model = Column(String(50), default="gpt-4", nullable=False)
    temperature = Column(Float, default=0.7, nullable=False)
    max_tokens = Column(Integer, default=1000, nullable=False)

    # Knowledge base
    knowledge_base_id = Column(String(255), nullable=True)  # ChromaDB collection ID
    custom_instructions = Column(Text, nullable=True)

    # Deployment information
    deployment_url = Column(String(500), nullable=True)
    deployment_key = Column(String(255), nullable=True)
    is_deployed = Column(Boolean, default=False, nullable=False)

    # Business metrics
    estimated_cost = Column(Float, nullable=True)
    actual_cost = Column(Float, default=0.0, nullable=False)
    estimated_completion = Column(DateTime(timezone=True), nullable=True)

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    deployed_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="chatbots")
    client = relationship("Client", back_populates="chatbots")
    conversations = relationship(
        "Conversation", back_populates="chatbot", cascade="all, delete-orphan"
    )
    knowledge_documents = relationship(
        "KnowledgeDocument", back_populates="chatbot", cascade="all, delete-orphan"
    )

    # Constraints and indexes
    __table_args__ = (
        Index("idx_chatbot_status", "status"),
        Index("idx_chatbot_type", "project_type"),
        Index("idx_chatbot_user", "user_id"),
        Index("idx_chatbot_client", "client_id"),
        Index("idx_chatbot_created", "created_at"),
        Index("idx_chatbot_deployed", "is_deployed"),
        CheckConstraint(
            "progress_percentage >= 0 AND progress_percentage <= 100",
            name="check_progress_range",
        ),
        CheckConstraint(
            "temperature >= 0 AND temperature <= 2", name="check_temperature_range"
        ),
        CheckConstraint("max_tokens > 0", name="check_max_tokens_positive"),
        CheckConstraint("estimated_cost >= 0", name="check_estimated_cost_positive"),
        CheckConstraint("actual_cost >= 0", name="check_actual_cost_positive"),
    )

    def __repr__(self):
        return f"<Chatbot(id={self.id}, name='{self.name}', status='{self.status}')>"


class Conversation(Base):
    """Conversation model for chat sessions"""

    __tablename__ = "conversations"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Conversation information
    title = Column(String(255), nullable=True)
    status = Column(
        SQLEnum(ConversationStatus), default=ConversationStatus.ACTIVE, nullable=False
    )

    # Session information
    session_id = Column(String(255), unique=True, index=True, nullable=False)
    user_ip = Column(String(45), nullable=True)  # IPv6 support
    user_agent = Column(String(500), nullable=True)
    referrer = Column(String(500), nullable=True)

    # Conversation metadata
    conversation_metadata = Column(JSON, nullable=True)
    context_data = Column(JSON, nullable=True)  # AI conversation context

    # Analytics and metrics
    message_count = Column(Integer, default=0, nullable=False)
    total_tokens_used = Column(Integer, default=0, nullable=False)
    total_cost = Column(Float, default=0.0, nullable=False)

    # Quality metrics
    satisfaction_score = Column(Float, nullable=True)  # 1-5 rating
    response_time_avg = Column(Float, nullable=True)  # Average response time in seconds

    # Foreign keys
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    chatbot_id = Column(Integer, ForeignKey("chatbots.id"), nullable=False)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    last_activity = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    ended_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="conversations")
    chatbot = relationship("Chatbot", back_populates="conversations")
    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="Message.created_at",
    )

    # Constraints and indexes
    __table_args__ = (
        Index("idx_conversation_session", "session_id"),
        Index("idx_conversation_status", "status"),
        Index("idx_conversation_user", "user_id"),
        Index("idx_conversation_chatbot", "chatbot_id"),
        Index("idx_conversation_created", "created_at"),
        Index("idx_conversation_activity", "last_activity"),
        CheckConstraint("message_count >= 0", name="check_message_count_positive"),
        CheckConstraint("total_tokens_used >= 0", name="check_tokens_positive"),
        CheckConstraint("total_cost >= 0", name="check_cost_positive"),
        CheckConstraint(
            "satisfaction_score IS NULL OR (satisfaction_score >= 1 AND satisfaction_score <= 5)",
            name="check_satisfaction_range",
        ),
    )

    def __repr__(self):
        return f"<Conversation(id={self.id}, session='{self.session_id}', status='{self.status}')>"


class Message(Base):
    """Message model for conversation messages"""

    __tablename__ = "messages"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Message content
    role = Column(SQLEnum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)

    # AI response metadata
    model_used = Column(String(50), nullable=True)
    tokens_used = Column(Integer, nullable=True)
    response_time = Column(Float, nullable=True)  # Response time in seconds
    cost = Column(Float, nullable=True)

    # Message metadata
    message_metadata = Column(JSON, nullable=True)
    is_edited = Column(Boolean, default=False, nullable=False)
    edit_count = Column(Integer, default=0, nullable=False)

    # Feedback and quality
    feedback_score = Column(Integer, nullable=True)  # 1-5 rating for individual message
    is_flagged = Column(Boolean, default=False, nullable=False)
    flag_reason = Column(String(255), nullable=True)

    # Foreign keys
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")

    # Constraints and indexes
    __table_args__ = (
        Index("idx_message_conversation", "conversation_id"),
        Index("idx_message_role", "role"),
        Index("idx_message_created", "created_at"),
        Index("idx_message_flagged", "is_flagged"),
        CheckConstraint(
            "tokens_used IS NULL OR tokens_used > 0", name="check_tokens_positive"
        ),
        CheckConstraint(
            "response_time IS NULL OR response_time >= 0",
            name="check_response_time_positive",
        ),
        CheckConstraint("cost IS NULL OR cost >= 0", name="check_cost_positive"),
        CheckConstraint(
            "feedback_score IS NULL OR (feedback_score >= 1 AND feedback_score <= 5)",
            name="check_feedback_range",
        ),
        CheckConstraint("edit_count >= 0", name="check_edit_count_positive"),
    )

    def __repr__(self):
        return f"<Message(id={self.id}, role='{self.role}', conversation_id={self.conversation_id})>"


class KnowledgeDocument(Base):
    """Knowledge base document model"""

    __tablename__ = "knowledge_documents"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Document information
    title = Column(String(255), nullable=False)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(20), nullable=False)  # pdf, txt, docx, etc.
    file_size = Column(Integer, nullable=False)  # Size in bytes

    # Content and processing
    content = Column(Text, nullable=True)  # Extracted text content
    summary = Column(Text, nullable=True)  # AI-generated summary
    keywords = Column(JSON, nullable=True)  # Extracted keywords

    # Vector storage information
    vector_id = Column(String(255), nullable=True)  # ChromaDB document ID
    embedding_model = Column(String(50), nullable=True)
    chunk_count = Column(Integer, default=0, nullable=False)

    # Processing status
    is_processed = Column(Boolean, default=False, nullable=False)
    processing_status = Column(
        String(50), default="pending", nullable=False
    )  # pending, processing, completed, failed
    processing_error = Column(Text, nullable=True)

    # Foreign keys
    chatbot_id = Column(Integer, ForeignKey("chatbots.id"), nullable=False)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    processed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    chatbot = relationship("Chatbot", back_populates="knowledge_documents")

    # Constraints and indexes
    __table_args__ = (
        Index("idx_knowledge_chatbot", "chatbot_id"),
        Index("idx_knowledge_processed", "is_processed"),
        Index("idx_knowledge_status", "processing_status"),
        Index("idx_knowledge_type", "file_type"),
        Index("idx_knowledge_created", "created_at"),
        CheckConstraint("file_size > 0", name="check_file_size_positive"),
        CheckConstraint("chunk_count >= 0", name="check_chunk_count_positive"),
    )

    def __repr__(self):
        return f"<KnowledgeDocument(id={self.id}, title='{self.title}', chatbot_id={self.chatbot_id})>"


# === ANALYTICS AND TRACKING MODELS ===


class ConversationAnalytics(Base):
    """Daily conversation analytics aggregation"""

    __tablename__ = "conversation_analytics"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Date and aggregation
    date = Column(DateTime(timezone=True), nullable=False)
    chatbot_id = Column(Integer, ForeignKey("chatbots.id"), nullable=False)

    # Conversation metrics
    total_conversations = Column(Integer, default=0, nullable=False)
    active_conversations = Column(Integer, default=0, nullable=False)
    completed_conversations = Column(Integer, default=0, nullable=False)

    # Message metrics
    total_messages = Column(Integer, default=0, nullable=False)
    user_messages = Column(Integer, default=0, nullable=False)
    assistant_messages = Column(Integer, default=0, nullable=False)

    # AI metrics
    total_tokens_used = Column(Integer, default=0, nullable=False)
    total_cost = Column(Float, default=0.0, nullable=False)
    avg_response_time = Column(Float, nullable=True)

    # Quality metrics
    avg_satisfaction = Column(Float, nullable=True)
    flagged_messages = Column(Integer, default=0, nullable=False)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Constraints and indexes
    __table_args__ = (
        Index("idx_analytics_date", "date"),
        Index("idx_analytics_chatbot", "chatbot_id"),
        UniqueConstraint("date", "chatbot_id", name="unique_daily_analytics"),
        CheckConstraint(
            "total_conversations >= 0", name="check_total_conversations_positive"
        ),
        CheckConstraint("total_messages >= 0", name="check_total_messages_positive"),
        CheckConstraint("total_tokens_used >= 0", name="check_total_tokens_positive"),
        CheckConstraint("total_cost >= 0", name="check_total_cost_positive"),
    )


class UserActivity(Base):
    """User activity tracking"""

    __tablename__ = "user_activity"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)

    # Activity information
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    activity_type = Column(
        String(50), nullable=False
    )  # login, logout, create_chatbot, etc.
    description = Column(String(500), nullable=True)

    # Request information
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    endpoint = Column(String(255), nullable=True)
    method = Column(String(10), nullable=True)

    # Additional data
    activity_metadata = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Constraints and indexes
    __table_args__ = (
        Index("idx_activity_user", "user_id"),
        Index("idx_activity_type", "activity_type"),
        Index("idx_activity_created", "created_at"),
        Index("idx_activity_ip", "ip_address"),
    )

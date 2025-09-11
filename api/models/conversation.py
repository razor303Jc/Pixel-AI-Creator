"""
Conversation Management Pydantic Models

Defines data models for conversation and message validation,
serialization, and API responses. Includes enums for status
tracking and comprehensive statistics models.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from enum import Enum
from pydantic import BaseModel, Field


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


# Conversation Models
class ConversationCreate(BaseModel):
    """Create new conversation request model"""

    project_id: int = Field(..., description="ID of the chatbot project")
    title: Optional[str] = Field(None, description="Conversation title")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional conversation metadata"
    )


class ConversationUpdate(BaseModel):
    """Update conversation request model"""

    title: Optional[str] = Field(None, description="Updated conversation title")
    status: Optional[ConversationStatus] = Field(
        None, description="Updated conversation status"
    )
    metadata: Optional[Dict[str, Any]] = Field(
        None, description="Updated conversation metadata"
    )


class ConversationSummary(BaseModel):
    """Conversation summary for list views"""

    id: int
    project_id: int
    title: str
    status: ConversationStatus
    message_count: int
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime] = None


class ConversationResponse(BaseModel):
    """Complete conversation response model"""

    id: int
    project_id: int
    user_id: int
    title: str
    status: ConversationStatus
    message_count: int
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime] = None
    messages: Optional[List["MessageResponse"]] = None


# Message Models
class MessageCreate(BaseModel):
    """Create new message request model"""

    content: str = Field(..., description="Message content")
    role: MessageRole = Field(..., description="Message role")
    metadata: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional message metadata"
    )


class MessageResponse(BaseModel):
    """Message response model"""

    id: int
    conversation_id: int
    content: str
    role: MessageRole
    metadata: Dict[str, Any]
    created_at: datetime


# Statistics Models
class ConversationStats(BaseModel):
    """Detailed conversation statistics"""

    conversation_id: int
    total_messages: int
    user_messages: int
    assistant_messages: int
    system_messages: int
    duration_minutes: int
    avg_response_time_seconds: float
    first_message_at: Optional[datetime] = None
    last_message_at: Optional[datetime] = None
    status: ConversationStatus


class MessageStats(BaseModel):
    """Message statistics for analytics"""

    total_messages: int
    user_messages: int
    assistant_messages: int
    system_messages: int
    avg_message_length: float
    most_active_hour: int
    busiest_day: str


# Update forward references
ConversationResponse.model_rebuild()

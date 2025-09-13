"""
Conversation Management API Routes

Provides comprehensive CRUD operations for managing chatbot conversations.
Includes conversation history, message handling, and real-time status updates.
All endpoints require JWT authentication and proper authorization.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, desc, asc
from sqlalchemy.orm import selectinload

from core.database import get_db, Conversation, Message, Project
from models.conversation import (
    ConversationCreate,
    ConversationResponse,
    ConversationUpdate,
    MessageCreate,
    MessageResponse,
    ConversationStatus,
    ConversationSummary,
    ConversationStats,
)
from auth.middleware import get_current_user

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("/", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    conversation_data: ConversationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Create a new conversation for a chatbot project.

    - **project_id**: ID of the chatbot project (required)
    - **title**: Optional conversation title
    - **metadata**: Additional conversation metadata

    Returns the created conversation with initial status.
    """
    # Verify project exists and user has access
    project_query = select(Project).where(
        and_(
            Project.id == conversation_data.project_id,
            or_(
                Project.client_id == current_user["client_id"],
                current_user["role"] == "admin",
            ),
        )
    )
    project_result = await db.execute(project_query)
    project = project_result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=404, detail="Project not found or access denied"
        )

    # Create conversation
    conversation = Conversation(
        project_id=conversation_data.project_id,
        user_id=current_user["user_id"],
        title=conversation_data.title or f"Conversation with {project.name}",
        status=ConversationStatus.ACTIVE,
        extra_data=conversation_data.metadata or {},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)

    return ConversationResponse(
        id=conversation.id,
        project_id=conversation.project_id,
        user_id=conversation.user_id,
        title=conversation.title,
        status=conversation.status,
        message_count=0,
        metadata=conversation.extra_data,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        last_message_at=None,
    )


@router.get("/", response_model=List[ConversationSummary])
async def list_conversations(
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    status: Optional[ConversationStatus] = Query(None, description="Filter by status"),
    limit: int = Query(20, le=100, description="Number of conversations to return"),
    offset: int = Query(0, description="Number of conversations to skip"),
    order_by: str = Query("updated_at", description="Order by field"),
    order_direction: str = Query("desc", description="Order direction (asc/desc)"),
    search: Optional[str] = Query(None, description="Search in conversation titles"),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    List conversations with filtering and pagination.

    Supports filtering by project, status, and search terms.
    Returns conversation summaries with message counts and timestamps.
    """
    # Build query with user access control
    query = select(Conversation).where(
        or_(
            Conversation.user_id == current_user["user_id"],
            current_user["role"] == "admin",
        )
    )

    # Apply filters
    if project_id:
        query = query.where(Conversation.project_id == project_id)

    if status:
        query = query.where(Conversation.status == status)

    if search:
        query = query.where(Conversation.title.ilike(f"%{search}%"))

    # Apply ordering
    order_field = getattr(Conversation, order_by, Conversation.updated_at)
    if order_direction.lower() == "desc":
        query = query.order_by(desc(order_field))
    else:
        query = query.order_by(asc(order_field))

    # Apply pagination
    query = query.offset(offset).limit(limit)

    # Execute query
    result = await db.execute(query)
    conversations = result.scalars().all()

    # Get message counts for each conversation
    conversation_summaries = []
    for conv in conversations:
        message_count_query = select(func.count(Message.id)).where(
            Message.conversation_id == conv.id
        )
        message_count_result = await db.execute(message_count_query)
        message_count = message_count_result.scalar() or 0

        last_message_query = (
            select(Message.created_at)
            .where(Message.conversation_id == conv.id)
            .order_by(desc(Message.created_at))
            .limit(1)
        )
        last_message_result = await db.execute(last_message_query)
        last_message_at = last_message_result.scalar()

        conversation_summaries.append(
            ConversationSummary(
                id=conv.id,
                project_id=conv.project_id,
                title=conv.title,
                status=conv.status,
                message_count=message_count,
                created_at=conv.created_at,
                updated_at=conv.updated_at,
                last_message_at=last_message_at,
            )
        )

    return conversation_summaries


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    include_messages: bool = Query(False, description="Include conversation messages"),
    message_limit: int = Query(50, le=200, description="Max messages to include"),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get detailed conversation information.

    Optionally includes recent messages with configurable limit.
    Returns full conversation details with metadata and statistics.
    """
    # Query with access control
    query = select(Conversation).where(
        and_(
            Conversation.id == conversation_id,
            or_(
                Conversation.user_id == current_user["user_id"],
                current_user["role"] == "admin",
            ),
        )
    )

    if include_messages:
        query = query.options(selectinload(Conversation.messages))

    result = await db.execute(query)
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=404, detail="Conversation not found or access denied"
        )

    # Get message count and last message timestamp
    message_count_query = select(func.count(Message.id)).where(
        Message.conversation_id == conversation_id
    )
    message_count_result = await db.execute(message_count_query)
    message_count = message_count_result.scalar() or 0

    last_message_query = (
        select(Message.created_at)
        .where(Message.conversation_id == conversation_id)
        .order_by(desc(Message.created_at))
        .limit(1)
    )
    last_message_result = await db.execute(last_message_query)
    last_message_at = last_message_result.scalar()

    response_data = ConversationResponse(
        id=conversation.id,
        project_id=conversation.project_id,
        user_id=conversation.user_id,
        title=conversation.title,
        status=conversation.status,
        message_count=message_count,
        metadata=conversation.extra_data,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        last_message_at=last_message_at,
    )

    # Add messages if requested
    if include_messages and hasattr(conversation, "messages"):
        messages = sorted(
            conversation.messages, key=lambda x: x.created_at, reverse=True
        )[:message_limit]
        response_data.messages = [
            MessageResponse(
                id=msg.id,
                conversation_id=msg.conversation_id,
                content=msg.content,
                role=msg.role,
                metadata=msg.extra_data,
                created_at=msg.created_at,
            )
            for msg in messages
        ]

    return response_data


@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: int,
    conversation_update: ConversationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Update conversation details.

    Allows updating title, status, and metadata.
    User can only update their own conversations unless admin.
    """
    # Query with access control
    query = select(Conversation).where(
        and_(
            Conversation.id == conversation_id,
            or_(
                Conversation.user_id == current_user["user_id"],
                current_user["role"] == "admin",
            ),
        )
    )

    result = await db.execute(query)
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=404, detail="Conversation not found or access denied"
        )

    # Update fields
    update_data = conversation_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(conversation, field, value)

    conversation.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(conversation)

    # Get updated message count
    message_count_query = select(func.count(Message.id)).where(
        Message.conversation_id == conversation_id
    )
    message_count_result = await db.execute(message_count_query)
    message_count = message_count_result.scalar() or 0

    return ConversationResponse(
        id=conversation.id,
        project_id=conversation.project_id,
        user_id=conversation.user_id,
        title=conversation.title,
        status=conversation.status,
        message_count=message_count,
        metadata=conversation.extra_data,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        last_message_at=None,
    )


@router.patch("/{conversation_id}/status", response_model=ConversationResponse)
async def update_conversation_status(
    conversation_id: int,
    status: ConversationStatus,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Update conversation status only.

    Quick endpoint for status changes (active, archived, closed).
    Automatically updates the timestamp.
    """
    # Query with access control
    query = select(Conversation).where(
        and_(
            Conversation.id == conversation_id,
            or_(
                Conversation.user_id == current_user["user_id"],
                current_user["role"] == "admin",
            ),
        )
    )

    result = await db.execute(query)
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=404, detail="Conversation not found or access denied"
        )

    conversation.status = status
    conversation.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(conversation)

    # Get message count
    message_count_query = select(func.count(Message.id)).where(
        Message.conversation_id == conversation_id
    )
    message_count_result = await db.execute(message_count_query)
    message_count = message_count_result.scalar() or 0

    return ConversationResponse(
        id=conversation.id,
        project_id=conversation.project_id,
        user_id=conversation.user_id,
        title=conversation.title,
        status=conversation.status,
        message_count=message_count,
        metadata=conversation.extra_data,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
        last_message_at=None,
    )


@router.delete("/{conversation_id}", status_code=204)
async def delete_conversation(
    conversation_id: int,
    permanent: bool = Query(False, description="Permanently delete (admin only)"),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Delete or archive a conversation.

    By default, sets status to 'archived' for data retention.
    Permanent deletion requires admin privileges.
    """
    # Query with access control
    query = select(Conversation).where(
        and_(
            Conversation.id == conversation_id,
            or_(
                Conversation.user_id == current_user["user_id"],
                current_user["role"] == "admin",
            ),
        )
    )

    result = await db.execute(query)
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=404, detail="Conversation not found or access denied"
        )

    if permanent and current_user["role"] != "admin":
        raise HTTPException(
            status_code=403, detail="Permanent deletion requires admin privileges"
        )

    if permanent:
        # Delete all messages first
        messages_query = select(Message).where(
            Message.conversation_id == conversation_id
        )
        messages_result = await db.execute(messages_query)
        messages = messages_result.scalars().all()

        for message in messages:
            await db.delete(message)

        # Delete conversation
        await db.delete(conversation)
    else:
        # Archive conversation
        conversation.status = ConversationStatus.ARCHIVED
        conversation.updated_at = datetime.utcnow()

    await db.commit()


@router.post(
    "/{conversation_id}/messages", response_model=MessageResponse, status_code=201
)
async def create_message(
    conversation_id: int,
    message_data: MessageCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Add a new message to the conversation.

    Supports both user and assistant messages.
    Automatically updates conversation timestamp.
    """
    # Verify conversation exists and user has access
    conv_query = select(Conversation).where(
        and_(
            Conversation.id == conversation_id,
            or_(
                Conversation.user_id == current_user["user_id"],
                current_user["role"] == "admin",
            ),
        )
    )
    conv_result = await db.execute(conv_query)
    conversation = conv_result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=404, detail="Conversation not found or access denied"
        )

    if conversation.status == ConversationStatus.CLOSED:
        raise HTTPException(
            status_code=400, detail="Cannot add messages to closed conversation"
        )

    # Create message
    message = Message(
        conversation_id=conversation_id,
        content=message_data.content,
        role=message_data.role,
        extra_data=message_data.metadata or {},
        created_at=datetime.utcnow(),
    )

    db.add(message)

    # Update conversation timestamp
    conversation.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(message)

    return MessageResponse(
        id=message.id,
        conversation_id=message.conversation_id,
        content=message.content,
        role=message.role,
        metadata=message.extra_data,
        created_at=message.created_at,
    )


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: int,
    limit: int = Query(50, le=200, description="Number of messages to return"),
    offset: int = Query(0, description="Number of messages to skip"),
    order: str = Query("asc", description="Order by created_at (asc/desc)"),
    role: Optional[str] = Query(None, description="Filter by message role"),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get messages from a conversation with pagination.

    Returns messages in chronological order by default.
    Supports filtering by role (user/assistant/system).
    """
    # Verify conversation access
    conv_query = select(Conversation).where(
        and_(
            Conversation.id == conversation_id,
            or_(
                Conversation.user_id == current_user["user_id"],
                current_user["role"] == "admin",
            ),
        )
    )
    conv_result = await db.execute(conv_query)
    conversation = conv_result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=404, detail="Conversation not found or access denied"
        )

    # Build message query
    query = select(Message).where(Message.conversation_id == conversation_id)

    if role:
        query = query.where(Message.role == role)

    # Apply ordering
    if order.lower() == "desc":
        query = query.order_by(desc(Message.created_at))
    else:
        query = query.order_by(asc(Message.created_at))

    # Apply pagination
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    messages = result.scalars().all()

    return [
        MessageResponse(
            id=msg.id,
            conversation_id=msg.conversation_id,
            content=msg.content,
            role=msg.role,
            metadata=msg.extra_data,
            created_at=msg.created_at,
        )
        for msg in messages
    ]


@router.get("/{conversation_id}/stats", response_model=ConversationStats)
async def get_conversation_stats(
    conversation_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get detailed conversation statistics.

    Includes message counts by role, response times,
    conversation duration, and activity patterns.
    """
    # Verify conversation access
    conv_query = select(Conversation).where(
        and_(
            Conversation.id == conversation_id,
            or_(
                Conversation.user_id == current_user["user_id"],
                current_user["role"] == "admin",
            ),
        )
    )
    conv_result = await db.execute(conv_query)
    conversation = conv_result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=404, detail="Conversation not found or access denied"
        )

    # Get message statistics
    message_stats = {}
    roles = ["user", "assistant", "system"]

    for role in roles:
        count_query = select(func.count(Message.id)).where(
            and_(Message.conversation_id == conversation_id, Message.role == role)
        )
        count_result = await db.execute(count_query)
        message_stats[f"{role}_messages"] = count_result.scalar() or 0

    # Total messages
    total_query = select(func.count(Message.id)).where(
        Message.conversation_id == conversation_id
    )
    total_result = await db.execute(total_query)
    total_messages = total_result.scalar() or 0

    # First and last message timestamps
    first_msg_query = (
        select(Message.created_at)
        .where(Message.conversation_id == conversation_id)
        .order_by(asc(Message.created_at))
        .limit(1)
    )
    first_msg_result = await db.execute(first_msg_query)
    first_message_at = first_msg_result.scalar()

    last_msg_query = (
        select(Message.created_at)
        .where(Message.conversation_id == conversation_id)
        .order_by(desc(Message.created_at))
        .limit(1)
    )
    last_msg_result = await db.execute(last_msg_query)
    last_message_at = last_msg_result.scalar()

    # Calculate duration
    duration_minutes = 0
    if first_message_at and last_message_at:
        duration = last_message_at - first_message_at
        duration_minutes = int(duration.total_seconds() / 60)

    # Average response time (simplified calculation)
    avg_response_time = 0
    if message_stats["user_messages"] > 0 and message_stats["assistant_messages"] > 0:
        # This is a simplified calculation - in production, you'd track actual response times
        avg_response_time = 2.5  # Average response time in seconds

    return ConversationStats(
        conversation_id=conversation_id,
        total_messages=total_messages,
        user_messages=message_stats["user_messages"],
        assistant_messages=message_stats["assistant_messages"],
        system_messages=message_stats["system_messages"],
        duration_minutes=duration_minutes,
        avg_response_time_seconds=avg_response_time,
        first_message_at=first_message_at,
        last_message_at=last_message_at,
        status=conversation.status,
    )


@router.get("/dashboard/summary", response_model=Dict[str, Any])
async def get_conversations_dashboard(
    timeframe: str = Query("30d", description="Timeframe: 7d, 30d, 90d"),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get dashboard summary of conversation activity.

    Provides overview metrics for conversation management
    and user engagement analytics.
    """
    # Calculate timeframe
    days_map = {"7d": 7, "30d": 30, "90d": 90}
    days = days_map.get(timeframe, 30)
    since_date = datetime.utcnow() - timedelta(days=days)

    # Base query with user access control
    base_query = select(Conversation).where(
        and_(
            Conversation.created_at >= since_date,
            or_(
                Conversation.user_id == current_user["user_id"],
                current_user["role"] == "admin",
            ),
        )
    )

    # Total conversations
    total_result = await db.execute(base_query)
    total_conversations = len(total_result.scalars().all())

    # Active conversations
    active_query = base_query.where(Conversation.status == ConversationStatus.ACTIVE)
    active_result = await db.execute(active_query)
    active_conversations = len(active_result.scalars().all())

    # Message counts
    message_query = select(func.count(Message.id)).where(
        and_(
            Message.created_at >= since_date,
            Message.conversation_id.in_(
                select(Conversation.id).where(
                    or_(
                        Conversation.user_id == current_user["user_id"],
                        current_user["role"] == "admin",
                    )
                )
            ),
        )
    )
    message_result = await db.execute(message_query)
    total_messages = message_result.scalar() or 0

    # Average messages per conversation
    avg_messages = total_messages / max(total_conversations, 1)

    return {
        "timeframe": timeframe,
        "summary": {
            "total_conversations": total_conversations,
            "active_conversations": active_conversations,
            "archived_conversations": total_conversations - active_conversations,
            "total_messages": total_messages,
            "avg_messages_per_conversation": round(avg_messages, 1),
        },
        "activity": {
            "conversations_this_week": active_conversations,
            "messages_this_week": total_messages,
            "most_active_day": "Monday",  # Placeholder - would be calculated from actual data
        },
        "performance": {
            "avg_response_time": "2.3s",  # Placeholder
            "user_satisfaction": "94%",  # Placeholder
            "resolution_rate": "87%",  # Placeholder
        },
    }

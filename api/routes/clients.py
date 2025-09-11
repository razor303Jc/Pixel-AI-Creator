"""
Client Management API Routes

This module provides CRUD operations for client management with authentication.
All endpoints require proper JWT authentication and role-based access control.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func, or_
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

# Import authentication
from auth.middleware import get_current_user

# Import database
from core.database import get_db, Client

# Import models
from models.client import ClientCreate, ClientUpdate, ClientStatus, ClientResponse

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/clients", tags=["clients"])


@router.post("/", response_model=ClientResponse)
async def create_client(
    client_data: ClientCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Create a new client.

    Requires authentication. Regular users can create clients.
    """
    try:
        # Check if client with this email already exists
        existing_client = await db.execute(
            select(Client).where(Client.email == client_data.email)
        )
        if existing_client.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Client with this email already exists",
            )

        # Create new client
        new_client = Client(
            name=client_data.name,
            email=client_data.email,
            company=client_data.company,
            website=client_data.website,
            phone=client_data.phone,
            industry=client_data.industry,
            description=client_data.description,
            twitter_handle=client_data.twitter_handle,
            instagram_handle=client_data.instagram_handle,
            linkedin_profile=client_data.linkedin_profile,
            status="active",
        )

        db.add(new_client)
        await db.commit()
        await db.refresh(new_client)

        logger.info(f"Client created: {new_client.email} by user {current_user.email}")
        return new_client

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating client: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create client",
        )


@router.get("/", response_model=List[ClientResponse])
async def list_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    industry: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    List clients with pagination and filtering.

    Supports:
    - Pagination with skip/limit
    - Search by name, email, or company
    - Filter by industry
    - Filter by status
    """
    try:
        # Build query
        query = select(Client)

        # Apply search filter
        if search:
            search_filter = or_(
                Client.name.ilike(f"%{search}%"),
                Client.email.ilike(f"%{search}%"),
                Client.company.ilike(f"%{search}%"),
            )
            query = query.where(search_filter)

        # Apply industry filter
        if industry:
            query = query.where(Client.industry == industry)

        # Apply status filter
        if status_filter:
            query = query.where(Client.status == status_filter)

        # Apply pagination
        query = query.offset(skip).limit(limit).order_by(Client.created_at.desc())

        # Execute query
        result = await db.execute(query)
        clients = result.scalars().all()

        logger.info(f"Listed {len(clients)} clients for user {current_user.email}")
        return clients

    except Exception as e:
        logger.error(f"Error listing clients: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list clients",
        )


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get a specific client by ID.
    """
    try:
        result = await db.execute(select(Client).where(Client.id == client_id))
        client = result.scalar_one_or_none()

        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Client not found"
            )

        logger.info(f"Retrieved client {client_id} by user {current_user.email}")
        return client

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving client {client_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve client",
        )


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    client_data: ClientUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Update a client's information.
    """
    try:
        # Get existing client
        result = await db.execute(select(Client).where(Client.id == client_id))
        client = result.scalar_one_or_none()

        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Client not found"
            )

        # Check for email conflicts if email is being updated
        if client_data.email and client_data.email != client.email:
            existing_email = await db.execute(
                select(Client).where(
                    Client.email == client_data.email, Client.id != client_id
                )
            )
            if existing_email.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already exists for another client",
                )

        # Update fields
        update_data = client_data.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.utcnow()

            await db.execute(
                update(Client).where(Client.id == client_id).values(**update_data)
            )
            await db.commit()

            # Refresh client
            await db.refresh(client)

        logger.info(f"Updated client {client_id} by user {current_user.email}")
        return client

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating client {client_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update client",
        )


@router.patch("/{client_id}/status", response_model=ClientResponse)
async def update_client_status(
    client_id: int,
    status_data: ClientStatus,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Update a client's status.

    Available statuses: active, inactive, suspended, pending
    """
    try:
        # Validate status
        valid_statuses = ["active", "inactive", "suspended", "pending"]
        if status_data.status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
            )

        # Get existing client
        result = await db.execute(select(Client).where(Client.id == client_id))
        client = result.scalar_one_or_none()

        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Client not found"
            )

        # Update status
        await db.execute(
            update(Client)
            .where(Client.id == client_id)
            .values(status=status_data.status, updated_at=datetime.utcnow())
        )
        await db.commit()
        await db.refresh(client)

        logger.info(
            f"Updated client {client_id} status to {status_data.status} by user {current_user.email}"
        )
        return client

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating client {client_id} status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update client status",
        )


@router.delete("/{client_id}")
async def delete_client(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Soft delete a client (set status to inactive).

    This preserves data integrity by not actually deleting the record.
    """
    try:
        # Get existing client
        result = await db.execute(select(Client).where(Client.id == client_id))
        client = result.scalar_one_or_none()

        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Client not found"
            )

        # Soft delete by setting status to inactive
        await db.execute(
            update(Client)
            .where(Client.id == client_id)
            .values(status="inactive", updated_at=datetime.utcnow())
        )
        await db.commit()

        logger.info(f"Soft deleted client {client_id} by user {current_user.email}")
        return {"message": "Client deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting client {client_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete client",
        )


@router.get("/stats/summary")
async def get_client_stats(
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get client statistics summary.
    """
    try:
        # Get total clients
        total_result = await db.execute(select(func.count(Client.id)))
        total_clients = total_result.scalar()

        # Get active clients
        active_result = await db.execute(
            select(func.count(Client.id)).where(Client.status == "active")
        )
        active_clients = active_result.scalar()

        # Get clients by status
        status_result = await db.execute(
            select(Client.status, func.count(Client.id)).group_by(Client.status)
        )
        status_breakdown = {status: count for status, count in status_result.all()}

        stats = {
            "total_clients": total_clients,
            "active_clients": active_clients,
            "status_breakdown": status_breakdown,
            "generated_at": datetime.utcnow(),
        }

        logger.info(f"Retrieved client stats for user {current_user.email}")
        return stats

    except Exception as e:
        logger.error(f"Error retrieving client stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve client statistics",
        )

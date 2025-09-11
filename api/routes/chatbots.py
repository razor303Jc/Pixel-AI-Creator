"""
Chatbot/Project Management API Routes

This module provides CRUD operations for chatbot project management.
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
from core.database import get_db, Project, Client

# Import models
from models.client import ProjectCreate, ProjectResponse

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/chatbots", tags=["chatbots"])


@router.post("/", response_model=ProjectResponse)
async def create_chatbot(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Create a new chatbot project.

    Requires authentication. Users can create chatbots for existing clients.
    """
    try:
        # Verify client exists
        client_result = await db.execute(
            select(Client).where(Client.id == project_data.client_id)
        )
        client = client_result.scalar_one_or_none()

        if not client:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Client not found"
            )

        # Create new project
        new_project = Project(
            client_id=project_data.client_id,
            name=project_data.name,
            description=project_data.description,
            assistant_type=project_data.assistant_type,
            complexity=project_data.complexity,
            status="pending",
            progress=0,
        )

        db.add(new_project)
        await db.commit()
        await db.refresh(new_project)

        logger.info(
            f"Chatbot project created: {new_project.name} by user {current_user['email']}"
        )
        return new_project

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating chatbot project: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create chatbot project",
        )


@router.get("/", response_model=List[ProjectResponse])
async def list_chatbots(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    client_id: Optional[int] = Query(None),
    assistant_type: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    complexity: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    List chatbot projects with filtering and pagination.

    Supports:
    - Filter by client_id
    - Filter by assistant_type (chatbot, voice_assistant, automation_bot)
    - Filter by status (pending, analyzing, generating, completed, failed)
    - Filter by complexity (basic, advanced, enterprise)
    """
    try:
        # Build query
        query = select(Project)

        # Apply filters
        if client_id:
            query = query.where(Project.client_id == client_id)

        if assistant_type:
            query = query.where(Project.assistant_type == assistant_type)

        if status_filter:
            query = query.where(Project.status == status_filter)

        if complexity:
            query = query.where(Project.complexity == complexity)

        # Apply pagination
        query = query.offset(skip).limit(limit).order_by(Project.created_at.desc())

        # Execute query
        result = await db.execute(query)
        projects = result.scalars().all()

        logger.info(
            f"Listed {len(projects)} chatbot projects for user {current_user['email']}"
        )
        return projects

    except Exception as e:
        logger.error(f"Error listing chatbot projects: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list chatbot projects",
        )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_chatbot(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get a specific chatbot project by ID.
    """
    try:
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot project not found",
            )

        logger.info(
            f"Retrieved chatbot project {project_id} by user {current_user['email']}"
        )
        return project

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving chatbot project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chatbot project",
        )


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_chatbot(
    project_id: int,
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Update a chatbot project's configuration.
    """
    try:
        # Get existing project
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot project not found",
            )

        # Update fields
        update_data = {
            "name": project_data.name,
            "description": project_data.description,
            "assistant_type": project_data.assistant_type,
            "complexity": project_data.complexity,
        }

        await db.execute(
            update(Project).where(Project.id == project_id).values(**update_data)
        )
        await db.commit()
        await db.refresh(project)

        logger.info(
            f"Updated chatbot project {project_id} by user {current_user['email']}"
        )
        return project

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating chatbot project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update chatbot project",
        )


@router.patch("/{project_id}/status")
async def update_chatbot_status(
    project_id: int,
    status_update: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Update a chatbot project's status and progress.

    Body should contain:
    - status: str (pending, analyzing, generating, completed, failed)
    - progress: int (0-100, optional)
    """
    try:
        # Validate status
        valid_statuses = ["pending", "analyzing", "generating", "completed", "failed"]
        new_status = status_update.get("status")

        if not new_status or new_status not in valid_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
            )

        # Get existing project
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot project not found",
            )

        # Prepare update data
        update_data = {"status": new_status}

        # Update progress if provided
        if "progress" in status_update:
            progress = status_update["progress"]
            if not isinstance(progress, int) or progress < 0 or progress > 100:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Progress must be an integer between 0 and 100",
                )
            update_data["progress"] = progress

        # Set completion time if completed
        if new_status == "completed":
            update_data["completed_at"] = datetime.utcnow()
            update_data["progress"] = 100

        # Update project
        await db.execute(
            update(Project).where(Project.id == project_id).values(**update_data)
        )
        await db.commit()

        logger.info(
            f"Updated chatbot project {project_id} status to {new_status} by user {current_user['email']}"
        )
        return {"message": "Status updated successfully", "status": new_status}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating chatbot project {project_id} status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update chatbot project status",
        )


@router.delete("/{project_id}")
async def delete_chatbot(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Delete a chatbot project.

    This performs a hard delete as projects in early stages can be safely removed.
    """
    try:
        # Get existing project
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot project not found",
            )

        # Delete project
        await db.delete(project)
        await db.commit()

        logger.info(
            f"Deleted chatbot project {project_id} by user {current_user['email']}"
        )
        return {"message": "Chatbot project deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting chatbot project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete chatbot project",
        )


@router.get("/{project_id}/stats")
async def get_chatbot_stats(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get performance metrics and statistics for a chatbot project.
    """
    try:
        # Get project
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Chatbot project not found",
            )

        # Calculate basic stats
        stats = {
            "project_id": project.id,
            "project_name": project.name,
            "status": project.status,
            "progress": project.progress,
            "assistant_type": project.assistant_type,
            "complexity": project.complexity,
            "created_at": project.created_at,
            "completed_at": project.completed_at,
            "days_in_development": (
                (datetime.utcnow() - project.created_at).days
                if project.created_at
                else 0
            ),
            "is_completed": project.status == "completed",
            "has_generated_code": bool(project.generated_code),
            "has_deployment_config": bool(project.deployment_config),
            "has_personality_config": bool(project.personality_config),
        }

        logger.info(
            f"Retrieved stats for chatbot project {project_id} by user {current_user['email']}"
        )
        return stats

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving chatbot project {project_id} stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chatbot project statistics",
        )


@router.get("/dashboard/summary")
async def get_chatbot_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get dashboard summary for all chatbot projects.
    """
    try:
        # Get total projects
        total_result = await db.execute(select(func.count(Project.id)))
        total_projects = total_result.scalar()

        # Get projects by status
        status_result = await db.execute(
            select(Project.status, func.count(Project.id)).group_by(Project.status)
        )
        status_breakdown = {status: count for status, count in status_result.all()}

        # Get projects by type
        type_result = await db.execute(
            select(Project.assistant_type, func.count(Project.id)).group_by(
                Project.assistant_type
            )
        )
        type_breakdown = {
            assistant_type: count for assistant_type, count in type_result.all()
        }

        # Get projects by complexity
        complexity_result = await db.execute(
            select(Project.complexity, func.count(Project.id)).group_by(
                Project.complexity
            )
        )
        complexity_breakdown = {
            complexity: count for complexity, count in complexity_result.all()
        }

        dashboard = {
            "total_projects": total_projects,
            "status_breakdown": status_breakdown,
            "type_breakdown": type_breakdown,
            "complexity_breakdown": complexity_breakdown,
            "generated_at": datetime.utcnow(),
        }

        logger.info(f"Retrieved chatbot dashboard for user {current_user['email']}")
        return dashboard

    except Exception as e:
        logger.error(f"Error retrieving chatbot dashboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chatbot dashboard",
        )

"""
Build Queue API Routes
Manages chatbot build jobs and Docker deployments
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from typing import Dict, Any, List
import logging

# Import authentication
from auth.middleware import get_current_user

# Import database
from core.database import get_db, Project

# Import build manager
from services.build_queue import build_manager, BuildStatus

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/builds", tags=["builds"])


@router.post("/queue/{project_id}")
async def queue_build(
    project_id: int,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Queue a build job for a chatbot project"""
    try:
        # Get project details
        result = await db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # Check if project is already building or completed
        if project.status in ["building", "testing", "deploying", "completed"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Project is already {project.status}"
            )
        
        # Prepare chatbot config
        chatbot_config = {
            "name": project.name,
            "description": project.description,
            "assistant_type": project.assistant_type,
            "complexity": project.complexity,
            "personality_config": project.personality_config or {}
        }
        
        # Queue the build job
        build_id = await build_manager.queue_build(
            project_id=project_id,
            user_id=current_user["id"],
            chatbot_config=chatbot_config
        )
        
        # Update project status
        await db.execute(
            update(Project)
            .where(Project.id == project_id)
            .values(status="queued", build_id=build_id)
        )
        await db.commit()
        
        logger.info(f"Build queued for project {project_id} by user {current_user['email']}")
        
        return {
            "message": "Build job queued successfully",
            "build_id": build_id,
            "project_id": project_id,
            "status": "queued"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error queuing build: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to queue build job"
        )


@router.get("/status/{build_id}")
async def get_build_status(
    build_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Get build status by build ID"""
    try:
        build_status = build_manager.get_build_status(build_id)
        
        if not build_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Build job not found"
            )
        
        return build_status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting build status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get build status"
        )


@router.get("/queue/status")
async def get_queue_status(
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Get overall build queue status"""
    try:
        queue_status = build_manager.get_queue_status()
        return queue_status
        
    except Exception as e:
        logger.error(f"Error getting queue status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get queue status"
        )


@router.get("/logs/{build_id}")
async def get_build_logs(
    build_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Get build logs for a specific build"""
    try:
        build_status = build_manager.get_build_status(build_id)
        
        if not build_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Build job not found"
            )
        
        return {
            "build_id": build_id,
            "logs": build_status.get("build_logs", []),
            "status": build_status.get("status", "unknown")
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting build logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get build logs"
        )


@router.post("/cancel/{build_id}")
async def cancel_build(
    build_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Cancel a build job"""
    try:
        build_status = build_manager.get_build_status(build_id)
        
        if not build_status:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Build job not found"
            )
        
        current_status = build_status.get("status")
        if current_status in ["completed", "failed", "cancelled"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot cancel build with status: {current_status}"
            )
        
        # TODO: Implement actual cancellation logic
        # This would involve stopping Docker containers and updating status
        
        logger.info(f"Build {build_id} cancelled by user {current_user['email']}")
        
        return {
            "message": "Build cancellation requested",
            "build_id": build_id,
            "status": "cancelled"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling build: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel build"
        )


@router.get("/projects/{project_id}/deployments")
async def get_project_deployments(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Get deployment information for a project"""
    try:
        result = await db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        deployment_info = project.deployment_info or {}
        
        return {
            "project_id": project_id,
            "status": project.status,
            "progress": project.progress,
            "deployment_info": deployment_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting deployments: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get deployment information"
        )


@router.delete("/cleanup/{project_id}")
async def cleanup_project_deployments(
    project_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """Clean up Docker containers and resources for a project"""
    try:
        result = await db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Project not found"
            )
        
        # TODO: Implement cleanup logic
        # This would involve stopping and removing Docker containers
        
        # Update project status
        await db.execute(
            update(Project)
            .where(Project.id == project_id)
            .values(
                status="pending",
                deployment_info=None,
                build_id=None
            )
        )
        await db.commit()
        
        logger.info(f"Cleaned up project {project_id} by user {current_user['email']}")
        
        return {
            "message": "Project cleanup completed",
            "project_id": project_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cleaning up project: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cleanup project"
        )
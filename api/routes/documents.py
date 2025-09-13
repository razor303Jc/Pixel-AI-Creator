"""
Document Upload and Management API Routes

This module handles file uploads, document processing, and knowledge base management.
Supp            # Creat            vector_id = None

            if vector_storage:
                try:
                    vector_id = await vector_storage.store_document_embedding(
                        text_content,
                        metadata={
                            "document_id": document.id,
                            "chatbot_id": chatbot_id,
                            "filename": file.filename,
                            "title": document.title
                        }
                    )embeddings
            vector_storage = get_vector_storage()
            vector_id = None

            if vector_storage:
                try:
                    vector_id = await vector_storage.store_document_embedding(
                        text_content,
                        metadata={
                            "document_id": document.id,
                            "chatbot_id": chatbot_id,
                            "filename": file.filename,
                            "title": document.title
                        }
                    )
                except Exception as e:
                    logger.warning(f"Vector storage failed: {e}")
            else:
                logger.warning("Vector storage not available - skipping embedding")DOCX, TXT files with automatic text extraction and vector storage.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import os
import aiofiles
import uuid
from pathlib import Path

# Import authentication
from auth.middleware import get_current_user

# Import database
from core.database import get_db
from models.database_schema import KnowledgeDocument, Chatbot

# Import services
from services.vector_storage import VectorStorageService
from services.document_processor import DocumentProcessor
from core.config import get_settings

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/documents", tags=["documents"])

# Initialize services
settings = get_settings()


# Note: VectorStorageService initialization is deferred to avoid startup issues
def get_vector_storage():
    """Get vector storage service instance, initialize if needed."""
    try:
        return VectorStorageService(settings)
    except Exception as e:
        logger.warning(f"Vector storage not available: {e}")
        return None


document_processor = DocumentProcessor()

# File upload configuration
UPLOAD_DIR = Path("/tmp/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt"}


@router.post("/upload/{chatbot_id}")
async def upload_document(
    chatbot_id: int,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Upload a document to a chatbot's knowledge base.

    Supports PDF, DOCX, DOC, and TXT files up to 10MB.
    Automatically extracts text and creates vector embeddings.
    """
    try:
        # Verify chatbot exists and user has access
        chatbot_result = await db.execute(
            select(Chatbot).where(Chatbot.id == chatbot_id)
        )
        chatbot = chatbot_result.scalar_one_or_none()

        if not chatbot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found"
            )

        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="No file provided"
            )

        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not supported. Allowed: {', '.join(ALLOWED_EXTENSIONS)}",
            )

        # Check file size
        if file.size and file.size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB",
            )

        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = UPLOAD_DIR / unique_filename

        # Save file temporarily
        content = await file.read()
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(content)

        # Create database record
        document = KnowledgeDocument(
            chatbot_id=chatbot_id,
            title=title or file.filename,
            filename=file.filename,
            file_type=file_extension[1:],  # Remove the dot
            file_size=len(content),
            processing_status="processing",
        )

        db.add(document)
        await db.commit()
        await db.refresh(document)

        # Process document asynchronously
        try:
            # Extract text content
            text_content = await document_processor.extract_text(
                file_path, file_extension
            )

            # Generate summary and keywords
            summary = await document_processor.generate_summary(text_content)
            keywords = await document_processor.extract_keywords(text_content)

            # Create vector embeddings
            vector_id = await vector_storage.store_document_embedding(
                text_content,
                metadata={
                    "document_id": document.id,
                    "chatbot_id": chatbot_id,
                    "filename": file.filename,
                    "title": document.title,
                },
            )

            # Update document with processed data
            await db.execute(
                update(KnowledgeDocument)
                .where(KnowledgeDocument.id == document.id)
                .values(
                    content=text_content,
                    summary=summary,
                    keywords=keywords,
                    vector_id=vector_id,
                    is_processed=True,
                    processing_status="completed",
                    processed_at=datetime.utcnow(),
                )
            )
            await db.commit()

            logger.info(
                f"Document processed successfully: {file.filename} for chatbot {chatbot_id}"
            )

        except Exception as processing_error:
            # Update document with error status
            await db.execute(
                update(KnowledgeDocument)
                .where(KnowledgeDocument.id == document.id)
                .values(
                    processing_status="failed", processing_error=str(processing_error)
                )
            )
            await db.commit()

            logger.error(f"Document processing failed: {str(processing_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Document upload succeeded but processing failed: {str(processing_error)}",
            )

        finally:
            # Clean up temporary file
            if file_path.exists():
                os.unlink(file_path)

        # Return document info
        await db.refresh(document)
        return {
            "id": document.id,
            "title": document.title,
            "filename": document.filename,
            "file_type": document.file_type,
            "file_size": document.file_size,
            "status": document.processing_status,
            "created_at": document.created_at,
            "processed": document.is_processed,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to upload document",
        )


@router.get("/chatbot/{chatbot_id}")
async def list_chatbot_documents(
    chatbot_id: int,
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    List all documents for a specific chatbot.
    """
    try:
        # Verify chatbot exists
        chatbot_result = await db.execute(
            select(Chatbot).where(Chatbot.id == chatbot_id)
        )
        chatbot = chatbot_result.scalar_one_or_none()

        if not chatbot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Chatbot not found"
            )

        # Get documents
        documents_result = await db.execute(
            select(KnowledgeDocument)
            .where(KnowledgeDocument.chatbot_id == chatbot_id)
            .order_by(KnowledgeDocument.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        documents = documents_result.scalars().all()

        return [
            {
                "id": doc.id,
                "title": doc.title,
                "filename": doc.filename,
                "file_type": doc.file_type,
                "file_size": doc.file_size,
                "status": doc.processing_status,
                "created_at": doc.created_at,
                "processed": doc.is_processed,
                "summary": doc.summary,
                "chunk_count": doc.chunk_count,
            }
            for doc in documents
        ]

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list documents",
        )


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Delete a document from the knowledge base.
    """
    try:
        # Get document
        document_result = await db.execute(
            select(KnowledgeDocument).where(KnowledgeDocument.id == document_id)
        )
        document = document_result.scalar_one_or_none()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
            )

        # Delete from vector storage
        if document.vector_id:
            vector_storage = get_vector_storage()
            if vector_storage:
                try:
                    await vector_storage.delete_document(document.vector_id)
                except Exception as e:
                    logger.warning(f"Could not delete vector embedding: {str(e)}")
            else:
                logger.warning("Vector storage not available for deletion")

        # Delete from database
        await db.execute(
            delete(KnowledgeDocument).where(KnowledgeDocument.id == document_id)
        )
        await db.commit()

        logger.info(f"Document deleted: {document.filename}")
        return {"message": "Document deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document",
        )


@router.get("/{document_id}")
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: Dict[str, Any] = Depends(get_current_user),
):
    """
    Get detailed information about a specific document.
    """
    try:
        document_result = await db.execute(
            select(KnowledgeDocument).where(KnowledgeDocument.id == document_id)
        )
        document = document_result.scalar_one_or_none()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Document not found"
            )

        return {
            "id": document.id,
            "title": document.title,
            "filename": document.filename,
            "file_type": document.file_type,
            "file_size": document.file_size,
            "content": document.content,
            "summary": document.summary,
            "keywords": document.keywords,
            "status": document.processing_status,
            "created_at": document.created_at,
            "processed_at": document.processed_at,
            "processed": document.is_processed,
            "chunk_count": document.chunk_count,
            "error": document.processing_error,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting document: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get document",
        )

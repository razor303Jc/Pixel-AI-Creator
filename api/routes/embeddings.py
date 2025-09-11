"""
API endpoints for vector storage and embedding operations.

This module provides REST API endpoints for:
- Storing conversation embeddings
- Searching similar conversations
- Managing knowledge bases
- Vector similarity search
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from services.vector_storage import VectorStorageService
from core.config import Settings


# Pydantic models for request/response
class StoreEmbeddingRequest(BaseModel):
    chatbot_id: str
    conversation_id: str
    message: str
    response: str
    metadata: Optional[Dict[str, Any]] = None


class SearchRequest(BaseModel):
    chatbot_id: str
    query: str
    n_results: int = 5


class StoreKnowledgeRequest(BaseModel):
    chatbot_id: str
    documents: List[str]
    metadata_list: Optional[List[Dict[str, Any]]] = None


class EmbeddingResponse(BaseModel):
    document_id: str
    status: str
    message: str


class SearchResponse(BaseModel):
    results: List[Dict[str, Any]]
    total_results: int


class HealthResponse(BaseModel):
    status: str
    details: Dict[str, Any]


# Router for embedding endpoints
router = APIRouter(prefix="/api/embeddings", tags=["embeddings"])


# Dependency to get vector storage service
def get_vector_service() -> VectorStorageService:
    settings = Settings()
    return VectorStorageService(settings)


@router.post("/store", response_model=EmbeddingResponse)
async def store_conversation_embedding(
    request: StoreEmbeddingRequest,
    vector_service: VectorStorageService = Depends(get_vector_service),
):
    """Store a conversation turn as an embedding for future similarity search.

    Args:
        request: Request containing conversation data to store
        vector_service: Vector storage service dependency

    Returns:
        Response with document ID and status
    """
    try:
        document_id = await vector_service.store_conversation_embedding(
            chatbot_id=request.chatbot_id,
            conversation_id=request.conversation_id,
            message=request.message,
            response=request.response,
            metadata=request.metadata,
        )

        return EmbeddingResponse(
            document_id=document_id,
            status="success",
            message="Conversation embedding stored successfully",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to store embedding: {str(e)}"
        )


@router.post("/search", response_model=SearchResponse)
async def search_similar_conversations(
    request: SearchRequest,
    vector_service: VectorStorageService = Depends(get_vector_service),
):
    """Search for similar conversations using vector similarity.

    Args:
        request: Search request with query and parameters
        vector_service: Vector storage service dependency

    Returns:
        Response with similar conversations and metadata
    """
    try:
        results = await vector_service.search_similar_conversations(
            chatbot_id=request.chatbot_id,
            query=request.query,
            n_results=request.n_results,
        )

        return SearchResponse(results=results, total_results=len(results))

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to search conversations: {str(e)}"
        )


@router.post("/knowledge", response_model=EmbeddingResponse)
async def store_knowledge_base(
    request: StoreKnowledgeRequest,
    vector_service: VectorStorageService = Depends(get_vector_service),
):
    """Store knowledge base documents for a chatbot.

    Args:
        request: Request containing documents to store
        vector_service: Vector storage service dependency

    Returns:
        Response with status and number of documents stored
    """
    try:
        document_ids = await vector_service.store_knowledge_base(
            chatbot_id=request.chatbot_id,
            documents=request.documents,
            metadata_list=request.metadata_list,
        )

        return EmbeddingResponse(
            document_id=f"{len(document_ids)}_documents",
            status="success",
            message=f"Stored {len(document_ids)} knowledge base documents",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to store knowledge base: {str(e)}"
        )


@router.post("/knowledge/search", response_model=SearchResponse)
async def search_knowledge_base(
    request: SearchRequest,
    vector_service: VectorStorageService = Depends(get_vector_service),
):
    """Search knowledge base for relevant information.

    Args:
        request: Search request with query and parameters
        vector_service: Vector storage service dependency

    Returns:
        Response with relevant knowledge base entries
    """
    try:
        results = await vector_service.search_knowledge_base(
            chatbot_id=request.chatbot_id,
            query=request.query,
            n_results=request.n_results,
        )

        return SearchResponse(results=results, total_results=len(results))

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to search knowledge base: {str(e)}"
        )


@router.delete("/collection/{chatbot_id}")
async def delete_chatbot_collection(
    chatbot_id: str, vector_service: VectorStorageService = Depends(get_vector_service)
):
    """Delete all embeddings for a specific chatbot.

    Args:
        chatbot_id: ID of the chatbot whose collection to delete
        vector_service: Vector storage service dependency

    Returns:
        Success message
    """
    try:
        success = vector_service.delete_collection(chatbot_id)

        if success:
            return {
                "status": "success",
                "message": f"Collection for chatbot {chatbot_id} deleted",
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to delete collection")

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to delete collection: {str(e)}"
        )


@router.get("/stats/{chatbot_id}")
async def get_collection_stats(
    chatbot_id: str, vector_service: VectorStorageService = Depends(get_vector_service)
):
    """Get statistics for a chatbot's embedding collection.

    Args:
        chatbot_id: ID of the chatbot
        vector_service: Vector storage service dependency

    Returns:
        Collection statistics
    """
    try:
        stats = vector_service.get_collection_stats(chatbot_id)
        return stats

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to get collection stats: {str(e)}"
        )


@router.get("/health", response_model=HealthResponse)
async def health_check(
    vector_service: VectorStorageService = Depends(get_vector_service),
):
    """Check the health of the vector storage service.

    Args:
        vector_service: Vector storage service dependency

    Returns:
        Health status and service information
    """
    try:
        health_info = vector_service.health_check()

        return HealthResponse(status=health_info["status"], details=health_info)

    except Exception as e:
        return HealthResponse(status="unhealthy", details={"error": str(e)})

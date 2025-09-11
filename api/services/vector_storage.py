"""
Vector Storage Service using ChromaDB for embeddings and similarity search.

This service provides:
- Storage of conversation embeddings
- Vector similarity search for context retrieval
- Collection management for different chatbots
- Integration with OpenAI embeddings
"""

import logging
import uuid
from typing import List, Dict, Optional, Any
import chromadb
import openai
from ..core.config import Settings as AppSettings

logger = logging.getLogger(__name__)


class VectorStorageService:
    """Service for managing vector embeddings and similarity search."""

    def __init__(self, settings: AppSettings):
        """Initialize the vector storage service.

        Args:
            settings: Application settings containing ChromaDB configuration
        """
        self.settings = settings
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize ChromaDB client."""
        try:
            self.client = chromadb.HttpClient(
                host=self.settings.chromadb_host, port=self.settings.chromadb_port
            )
            logger.info(
                f"Connected to ChromaDB at "
                f"{self.settings.chromadb_host}:{self.settings.chromadb_port}"
            )
        except Exception as e:
            logger.error(f"Failed to connect to ChromaDB: {e}")
            raise

    def get_or_create_collection(self, chatbot_id: str) -> chromadb.Collection:
        """Get or create a collection for a specific chatbot.

        Args:
            chatbot_id: Unique identifier for the chatbot

        Returns:
            ChromaDB collection for the chatbot
        """
        collection_name = f"chatbot_{chatbot_id}"
        try:
            # Try to get existing collection
            collection = self.client.get_collection(name=collection_name)
            logger.info(f"Retrieved existing collection: {collection_name}")
        except Exception:
            # Create new collection if it doesn't exist
            collection = self.client.create_collection(
                name=collection_name, metadata={"chatbot_id": chatbot_id}
            )
            logger.info(f"Created new collection: {collection_name}")

        return collection

    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using OpenAI's text-embedding-ada-002 model.

        Args:
            texts: List of texts to generate embeddings for

        Returns:
            List of embedding vectors
        """
        try:
            openai.api_key = self.settings.openai_api_key
            response = await openai.embeddings.acreate(
                input=texts, model="text-embedding-ada-002"
            )

            embeddings = [data.embedding for data in response.data]
            logger.info(f"Generated {len(embeddings)} embeddings")
            return embeddings

        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise

    async def store_conversation_embedding(
        self,
        chatbot_id: str,
        conversation_id: str,
        message: str,
        response: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Store a conversation turn as an embedding.

        Args:
            chatbot_id: ID of the chatbot
            conversation_id: ID of the conversation
            message: User message
            response: Bot response
            metadata: Additional metadata to store

        Returns:
            Document ID of the stored embedding
        """
        try:
            collection = self.get_or_create_collection(chatbot_id)

            # Combine message and response for embedding
            text_to_embed = f"User: {message}\nBot: {response}"

            # Generate embedding
            embeddings = await self.generate_embeddings([text_to_embed])

            # Prepare metadata
            doc_metadata = {
                "conversation_id": conversation_id,
                "chatbot_id": chatbot_id,
                "user_message": message,
                "bot_response": response,
                "timestamp": str(uuid.uuid4()),  # Simple timestamp
            }

            if metadata:
                doc_metadata.update(metadata)

            # Generate unique document ID
            doc_id = str(uuid.uuid4())

            # Store in ChromaDB
            collection.add(
                embeddings=embeddings,
                documents=[text_to_embed],
                metadatas=[doc_metadata],
                ids=[doc_id],
            )

            logger.info(f"Stored embedding for conversation {conversation_id}")
            return doc_id

        except Exception as e:
            logger.error(f"Failed to store conversation embedding: {e}")
            raise

    async def search_similar_conversations(
        self, chatbot_id: str, query: str, n_results: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar conversations using vector similarity.

        Args:
            chatbot_id: ID of the chatbot to search within
            query: Query text to find similar conversations
            n_results: Number of results to return

        Returns:
            List of similar conversation metadata and distances
        """
        try:
            collection = self.get_or_create_collection(chatbot_id)

            # Generate embedding for query
            query_embeddings = await self.generate_embeddings([query])

            # Search for similar embeddings
            results = collection.query(
                query_embeddings=query_embeddings, n_results=n_results
            )

            # Format results
            formatted_results = []
            for i in range(len(results["ids"][0])):
                result = {
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                }
                formatted_results.append(result)

            logger.info(f"Found {len(formatted_results)} similar conversations")
            return formatted_results

        except Exception as e:
            logger.error(f"Failed to search similar conversations: {e}")
            raise

    async def store_knowledge_base(
        self,
        chatbot_id: str,
        documents: List[str],
        metadata_list: Optional[List[Dict[str, Any]]] = None,
    ) -> List[str]:
        """Store knowledge base documents for a chatbot.

        Args:
            chatbot_id: ID of the chatbot
            documents: List of documents to store
            metadata_list: Optional metadata for each document

        Returns:
            List of document IDs
        """
        try:
            collection = self.get_or_create_collection(chatbot_id)

            # Generate embeddings for all documents
            embeddings = await self.generate_embeddings(documents)

            # Generate document IDs
            doc_ids = [str(uuid.uuid4()) for _ in documents]

            # Prepare metadata
            if metadata_list is None:
                metadata_list = [{"type": "knowledge_base"} for _ in documents]
            else:
                for metadata in metadata_list:
                    metadata["type"] = "knowledge_base"

            # Store in ChromaDB
            collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadata_list,
                ids=doc_ids,
            )

            logger.info(f"Stored {len(documents)} knowledge base documents")
            return doc_ids

        except Exception as e:
            logger.error(f"Failed to store knowledge base: {e}")
            raise

    async def search_knowledge_base(
        self, chatbot_id: str, query: str, n_results: int = 3
    ) -> List[Dict[str, Any]]:
        """Search knowledge base for relevant information.

        Args:
            chatbot_id: ID of the chatbot
            query: Query to search for
            n_results: Number of results to return

        Returns:
            List of relevant knowledge base entries
        """
        try:
            collection = self.get_or_create_collection(chatbot_id)

            # Generate embedding for query
            query_embeddings = await self.generate_embeddings([query])

            # Search with filter for knowledge base documents
            results = collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                where={"type": "knowledge_base"},
            )

            # Format results
            formatted_results = []
            for i in range(len(results["ids"][0])):
                result = {
                    "id": results["ids"][0][i],
                    "document": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i],
                }
                formatted_results.append(result)

            logger.info(
                f"Found {len(formatted_results)} relevant knowledge base entries"
            )
            return formatted_results

        except Exception as e:
            logger.error(f"Failed to search knowledge base: {e}")
            raise

    def delete_collection(self, chatbot_id: str) -> bool:
        """Delete a chatbot's collection.

        Args:
            chatbot_id: ID of the chatbot

        Returns:
            True if deletion was successful
        """
        collection_name = f"chatbot_{chatbot_id}"
        try:
            self.client.delete_collection(name=collection_name)
            logger.info(f"Deleted collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection {collection_name}: {e}")
            return False

    def get_collection_stats(self, chatbot_id: str) -> Dict[str, Any]:
        """Get statistics for a chatbot's collection.

        Args:
            chatbot_id: ID of the chatbot

        Returns:
            Dictionary with collection statistics
        """
        try:
            collection = self.get_or_create_collection(chatbot_id)
            count = collection.count()

            return {
                "chatbot_id": chatbot_id,
                "total_documents": count,
                "collection_name": f"chatbot_{chatbot_id}",
            }

        except Exception as e:
            logger.error(f"Failed to get collection stats: {e}")
            return {"error": str(e)}

    def health_check(self) -> Dict[str, Any]:
        """Check the health of the vector storage service.

        Returns:
            Health status information
        """
        try:
            # Test connection by listing collections
            collections = self.client.list_collections()

            return {
                "status": "healthy",
                "chromadb_host": self.settings.chromadb_host,
                "chromadb_port": self.settings.chromadb_port,
                "total_collections": len(collections),
                "collections": [col.name for col in collections],
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "chromadb_host": self.settings.chromadb_host,
                "chromadb_port": self.settings.chromadb_port,
            }

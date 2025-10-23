"""Vector Database Service using ChromaDB"""
from typing import Dict, List, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.core.config import settings


class VectorDBService:
    """ChromaDB vector database service"""

    def __init__(self):
        """Initialize ChromaDB client"""
        self.client = chromadb.Client(
            ChromaSettings(
                persist_directory=settings.CHROMADB_PATH,
                anonymized_telemetry=False
            )
        )
        self.collection_name = settings.CHROMADB_COLLECTION_NAME

    def get_or_create_collection(self, document_id: str) -> chromadb.Collection:
        """
        Get or create a collection for a document.

        Args:
            document_id: Document ID to create collection for

        Returns:
            ChromaDB collection instance
        """
        collection_name = f"{self.collection_name}_{document_id}"
        return self.client.get_or_create_collection(
            name=collection_name,
            metadata={"document_id": document_id}
        )

    async def add_chunks(
        self,
        document_id: str,
        chunk_ids: List[str],
        embeddings: List[List[float]],
        contents: List[str],
        metadatas: Optional[List[Dict]] = None
    ) -> None:
        """
        Add document chunks to the vector database.

        Args:
            document_id: Document ID
            chunk_ids: List of chunk IDs
            embeddings: List of embedding vectors
            contents: List of chunk text contents
            metadatas: Optional list of metadata dicts for each chunk
        """
        collection = self.get_or_create_collection(document_id)

        collection.add(
            ids=chunk_ids,
            embeddings=embeddings,
            documents=contents,
            metadatas=metadatas or [{}] * len(chunk_ids)
        )

    async def search_similar(
        self,
        document_id: str,
        query_embedding: List[float],
        n_results: int = 5,
        where: Optional[Dict] = None
    ) -> Dict:
        """
        Search for similar chunks using vector similarity.

        Args:
            document_id: Document ID to search within
            query_embedding: Query embedding vector
            n_results: Number of results to return
            where: Optional metadata filter

        Returns:
            Dict containing 'ids', 'distances', 'documents', and 'metadatas'
        """
        collection = self.get_or_create_collection(document_id)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where
        )

        return {
            "ids": results["ids"][0] if results["ids"] else [],
            "distances": results["distances"][0] if results["distances"] else [],
            "documents": results["documents"][0] if results["documents"] else [],
            "metadatas": results["metadatas"][0] if results["metadatas"] else [],
        }

    async def delete_document(self, document_id: str) -> None:
        """
        Delete all chunks for a document.

        Args:
            document_id: Document ID to delete
        """
        try:
            collection_name = f"{self.collection_name}_{document_id}"
            self.client.delete_collection(name=collection_name)
        except ValueError:
            # Collection doesn't exist, ignore
            pass

    async def get_chunk(self, document_id: str, chunk_id: str) -> Optional[Dict]:
        """
        Get a specific chunk by ID.

        Args:
            document_id: Document ID
            chunk_id: Chunk ID

        Returns:
            Dict with chunk data or None if not found
        """
        collection = self.get_or_create_collection(document_id)

        results = collection.get(
            ids=[chunk_id],
            include=["embeddings", "documents", "metadatas"]
        )

        if not results["ids"]:
            return None

        return {
            "id": results["ids"][0],
            "embedding": results["embeddings"][0] if results["embeddings"] else None,
            "document": results["documents"][0] if results["documents"] else None,
            "metadata": results["metadatas"][0] if results["metadatas"] else None,
        }

    def get_collection_count(self, document_id: str) -> int:
        """
        Get the number of chunks in a document's collection.

        Args:
            document_id: Document ID

        Returns:
            Number of chunks
        """
        try:
            collection = self.get_or_create_collection(document_id)
            return collection.count()
        except ValueError:
            return 0

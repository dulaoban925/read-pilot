"""
Vector database and semantic search tools
"""
from parlant import tool, ToolContext, ToolResult
from typing import List, Dict, Optional
from config import settings
import httpx


@tool
async def semantic_search(
    context: ToolContext,
    query: str,
    document_id: Optional[str] = None,
    top_k: int = 5
) -> ToolResult:
    """
    Perform semantic search on document content

    Args:
        context: Parlant tool context
        query: Search query
        document_id: Optional document to search within
        top_k: Number of results to return

    Returns:
        List of relevant passages
    """
    try:
        # Get query embedding
        query_embedding = await embed_text(context, query)

        if not query_embedding.success:
            return ToolResult(
                success=False,
                message="Failed to generate query embedding"
            )

        # Build search filter
        search_filter = {}
        if document_id:
            search_filter["document_id"] = document_id

        # Perform vector search (placeholder - implement actual vector DB query)
        # This would typically call Pinecone, Qdrant, or similar
        results = await _vector_db_search(
            embedding=query_embedding.data["embedding"],
            filter=search_filter,
            top_k=top_k
        )

        # Store retrieved passages in context for later use
        context.variables["retrieved_passages"] = results

        return ToolResult(
            success=True,
            data={
                "passages": results,
                "count": len(results)
            }
        )

    except Exception as e:
        return ToolResult(
            success=False,
            message=f"Semantic search failed: {str(e)}"
        )


@tool
async def embed_text(
    context: ToolContext,
    text: str
) -> ToolResult:
    """
    Generate embedding for text

    Args:
        context: Parlant tool context
        text: Text to embed

    Returns:
        Text embedding vector
    """
    try:
        if settings.DEFAULT_LLM_PROVIDER == "openai":
            embedding = await _openai_embed(text)
        else:
            # Fallback to local model
            embedding = await _local_embed(text)

        return ToolResult(
            success=True,
            data={"embedding": embedding}
        )

    except Exception as e:
        return ToolResult(
            success=False,
            message=f"Embedding generation failed: {str(e)}"
        )


async def _openai_embed(text: str) -> List[float]:
    """Generate embedding using OpenAI API"""
    import openai

    openai.api_key = settings.OPENAI_API_KEY

    response = await openai.embeddings.create(
        model=settings.EMBEDDING_MODEL,
        input=text
    )

    return response.data[0].embedding


async def _local_embed(text: str) -> List[float]:
    """Generate embedding using local sentence-transformers model"""
    from sentence_transformers import SentenceTransformer

    # Load model (should be cached after first load)
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embedding = model.encode(text)

    return embedding.tolist()


async def _vector_db_search(
    embedding: List[float],
    filter: Dict,
    top_k: int = 5
) -> List[Dict]:
    """
    Perform vector similarity search using Qdrant

    Production implementation:
    - Connect to Qdrant vector database
    - Perform similarity search
    - Return ranked results
    """

    # TODO: Implement Qdrant search
    # from qdrant_client import QdrantClient
    # from qdrant_client.models import Filter, FieldCondition, MatchValue
    #
    # client = QdrantClient(url=settings.QDRANT_URL)
    #
    # # Build Qdrant filter
    # qdrant_filter = None
    # if filter.get("document_id"):
    #     qdrant_filter = Filter(
    #         must=[FieldCondition(key="document_id", match=MatchValue(value=filter["document_id"]))]
    #     )
    #
    # results = client.search(
    #     collection_name=settings.QDRANT_COLLECTION_NAME,
    #     query_vector=embedding,
    #     query_filter=qdrant_filter,
    #     limit=top_k
    # )

    # Placeholder return
    return [
        {
            "text": "Sample passage 1...",
            "page": 1,
            "score": 0.95,
            "document_id": filter.get("document_id", "unknown")
        },
        {
            "text": "Sample passage 2...",
            "page": 3,
            "score": 0.89,
            "document_id": filter.get("document_id", "unknown")
        },
    ]


async def index_document(
    document_id: str,
    chunks: List[Dict[str, any]]
) -> bool:
    """
    Index document chunks into vector database

    Args:
        document_id: Document identifier
        chunks: List of text chunks with metadata

    Returns:
        Success status
    """
    try:
        # Generate embeddings for all chunks
        embeddings = []
        for chunk in chunks:
            embedding = await _openai_embed(chunk["text"])
            embeddings.append({
                "id": f"{document_id}_{chunk['chunk_id']}",
                "values": embedding,
                "metadata": {
                    "document_id": document_id,
                    "text": chunk["text"],
                    "page": chunk.get("page", 0),
                    "chunk_id": chunk["chunk_id"]
                }
            })

        # Insert into Qdrant vector database
        # TODO: Implement actual insertion
        # from qdrant_client import QdrantClient
        # from qdrant_client.models import PointStruct
        #
        # client = QdrantClient(url=settings.QDRANT_URL)
        # points = [
        #     PointStruct(
        #         id=emb["id"],
        #         vector=emb["values"],
        #         payload=emb["metadata"]
        #     )
        #     for emb in embeddings
        # ]
        # client.upsert(collection_name=settings.QDRANT_COLLECTION_NAME, points=points)

        return True

    except Exception as e:
        print(f"Failed to index document: {str(e)}")
        return False

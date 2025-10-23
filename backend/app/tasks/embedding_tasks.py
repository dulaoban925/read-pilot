"""Embedding生成Celery任务"""
from sqlalchemy import select

from app.core.ai import get_embedding_service
from app.core.vector_db import VectorDBService
from app.db.session import async_session_maker
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.tasks.celery_app import celery_app


@celery_app.task(name="generate_embeddings", bind=True)
def generate_embeddings_task(self, document_id: str):
    """
    生成文档chunks的embeddings并存储到向量数据库

    Args:
        document_id: 文档ID
    """
    import asyncio
    return asyncio.run(_generate_embeddings(document_id))


async def _generate_embeddings(document_id: str):
    """异步生成embeddings"""
    async with async_session_maker() as db:
        # 获取文档
        result = await db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()

        if not document:
            raise ValueError(f"Document not found: {document_id}")

        # 获取所有chunks
        chunks_result = await db.execute(
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index)
        )
        chunks = chunks_result.scalars().all()

        if not chunks:
            raise ValueError(f"No chunks found for document: {document_id}")

        try:
            # 获取embedding服务
            embedding_service = get_embedding_service()

            # 批量生成embeddings
            contents = [chunk.content for chunk in chunks]
            embeddings = await embedding_service.generate_embeddings(contents)

            # 存储到向量数据库
            vector_service = VectorDBService()

            chunk_ids = [chunk.id for chunk in chunks]
            metadatas = [
                {
                    "document_id": document_id,
                    "chunk_index": chunk.chunk_index,
                    "token_count": chunk.token_count,
                    **(chunk.location_metadata or {})
                }
                for chunk in chunks
            ]

            await vector_service.add_chunks(
                document_id=document_id,
                chunk_ids=chunk_ids,
                embeddings=embeddings,
                contents=contents,
                metadatas=metadatas
            )

            # 获取模型名称
            model_name = getattr(embedding_service, 'model', 'text-embedding-v3')

            # 更新chunks的embedding_id
            for i, chunk in enumerate(chunks):
                chunk.embedding_id = chunk_ids[i]
                chunk.embedding_model = model_name

            # 更新文档为已索引
            document.is_indexed = True
            await db.commit()

            return {
                "status": "success",
                "document_id": document_id,
                "embeddings_count": len(embeddings),
            }

        except Exception as e:
            raise RuntimeError(f"Failed to generate embeddings: {str(e)}")

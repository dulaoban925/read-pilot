"""文档处理Celery任务"""
import uuid
from pathlib import Path

from sqlalchemy import select

from app.core.document_parser import document_parser_factory
from app.core.text_chunker import text_chunker
from app.db.session import async_session_maker
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.tasks.celery_app import celery_app


@celery_app.task(name="process_document", bind=True)
def process_document_task(self, document_id: str):
    """
    处理文档任务：解析、分块、生成embedding

    Args:
        document_id: 文档ID
    """
    import asyncio
    return asyncio.run(_process_document(document_id))


async def _process_document(document_id: str):
    """异步处理文档"""
    async with async_session_maker() as db:
        # 获取文档
        result = await db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()

        if not document:
            raise ValueError(f"Document not found: {document_id}")

        try:
            # 更新状态为processing
            document.processing_status = "processing"
            await db.commit()

            # 解析文档
            file_path = Path(document.file_path)
            parsed_doc = await document_parser_factory.parse_document(file_path)

            # 更新文档元数据
            document.word_count = parsed_doc.word_count
            document.page_count = parsed_doc.page_count
            if parsed_doc.metadata.get("author"):
                document.author = parsed_doc.metadata["author"]

            # 分块
            chunks_data = text_chunker.chunk_with_metadata(
                parsed_doc.text,
                metadata={
                    "document_id": document_id,
                    "file_type": document.file_type,
                }
            )

            # 保存chunks到数据库
            for chunk_data in chunks_data:
                chunk = DocumentChunk(
                    id=str(uuid.uuid4()),
                    document_id=document_id,
                    content=chunk_data["content"],
                    token_count=chunk_data["token_count"],
                    chunk_index=chunk_data["chunk_index"],
                    location_metadata=chunk_data["metadata"]
                )
                db.add(chunk)

            # 更新状态为completed
            document.processing_status = "completed"
            document.processing_error = None
            await db.commit()

            # 触发embedding生成任务
            from app.tasks.embedding_tasks import generate_embeddings_task
            generate_embeddings_task.delay(document_id)

            return {
                "status": "success",
                "document_id": document_id,
                "chunks_count": len(chunks_data),
                "word_count": document.word_count,
                "page_count": document.page_count,
            }

        except Exception as e:
            # 更新状态为failed
            document.processing_status = "failed"
            document.processing_error = str(e)
            await db.commit()

            raise


@celery_app.task(name="generate_summary", bind=True)
def generate_summary_task(self, document_id: str, depth: str = "detailed"):
    """
    生成文档摘要任务

    Args:
        document_id: 文档 ID
        depth: 摘要深度 (brief/detailed)
    """
    import asyncio
    return asyncio.run(_generate_summary(document_id, depth))


async def _generate_summary(document_id: str, depth: str = "detailed"):
    """异步生成摘要"""
    from app.services.summary_service import SummaryService

    async with async_session_maker() as db:
        # 获取文档
        result = await db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()

        if not document:
            raise ValueError(f"Document not found: {document_id}")

        try:
            # 创建摘要服务
            summary_service = SummaryService(db)

            # 生成摘要
            summary = await summary_service.generate_summary(document, depth)

            return {
                "status": "success",
                "document_id": document_id,
                "summary_id": str(summary.id),
                "depth": depth,
            }

        except Exception as e:
            # 记录错误
            import logging
            logger = logging.getLogger(__name__)
            logger.error(
                f"Failed to generate summary for document {document_id}: {str(e)}"
            )
            raise

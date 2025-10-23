"""
摘要服务 (Summary Service)

处理文档摘要的业务逻辑:
- 生成摘要
- 获取摘要
- 缓存管理
"""

from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.cache import get_cache_service
from app.models.ai_summary import AISummary
from app.models.document import Document
from app.models.user import User
from app.schemas.document import SummaryCreate, SummaryResponse
from app.services.ai_service import get_ai_service
from app.utils.logger import get_logger

logger = get_logger(__name__)


class SummaryService:
    """摘要服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai_service = get_ai_service()
        self.cache = get_cache_service()
        self._cache_initialized = False

    async def _ensure_cache_connected(self):
        """确保缓存已连接"""
        if not self._cache_initialized:
            try:
                await self.cache.connect()
                self._cache_initialized = True
            except Exception as e:
                logger.warning("cache_connection_failed", error=str(e))

    async def _safe_cache_get(self, key: str) -> Optional[str]:
        """安全地从缓存获取数据"""
        try:
            await self._ensure_cache_connected()
            return await self.cache.get(key)
        except Exception as e:
            logger.warning("cache_get_failed", key=key, error=str(e))
            return None

    async def _safe_cache_set(self, key: str, value: str, expire: int = 3600):
        """安全地设置缓存数据"""
        try:
            await self._ensure_cache_connected()
            await self.cache.set(key, value, expire=expire)
        except Exception as e:
            logger.warning("cache_set_failed", key=key, error=str(e))

    async def get_summary(
        self, document_id: UUID, user: User
    ) -> Optional[AISummary]:
        """
        获取文档摘要

        Args:
            document_id: 文档 ID
            user: 用户对象

        Returns:
            摘要对象或 None
        """
        # 检查缓存
        cache_key = f"summary:{document_id}"
        cached = await self._safe_cache_get(cache_key)
        if cached:
            logger.info("summary_cache_hit", document_id=str(document_id))
            # 从数据库获取完整对象
            stmt = select(AISummary).where(AISummary.document_id == document_id)
            result = await self.db.execute(stmt)
            return result.scalar_one_or_none()

        # 从数据库查询
        stmt = (
            select(AISummary)
            .join(Document)
            .where(
                AISummary.document_id == document_id, Document.user_id == user.id
            )
        )
        result = await self.db.execute(stmt)
        summary = result.scalar_one_or_none()

        if summary:
            # 更新缓存
            await self._safe_cache_set(cache_key, "1", expire=7 * 24 * 3600)

        return summary

    async def generate_summary(
        self, document: Document, depth: str = "detailed"
    ) -> AISummary:
        """
        生成文档摘要

        Args:
            document: 文档对象
            depth: 摘要深度

        Returns:
            生成的摘要对象
        """
        logger.info(
            "generating_summary",
            document_id=str(document.id),
            depth=depth,
            file_type=document.file_type,
        )

        # 读取文档内容
        from pathlib import Path
        from app.core.document_parser import document_parser_factory

        try:
            file_path = Path(document.file_path)

            # 优先从文件读取完整内容
            if file_path.exists() and file_path.is_file():
                try:
                    logger.info("parsing_document_file", file_path=str(file_path))
                    parsed_doc = await document_parser_factory.parse_document(file_path)
                    text_content = parsed_doc.text
                    logger.info("document_parsed_successfully",
                               file_path=str(file_path),
                               text_length=len(text_content))
                except Exception as parse_error:
                    logger.warning("document_parse_failed",
                                 file_path=str(file_path),
                                 error=str(parse_error))
                    # 解析失败时降级到 chunks
                    text_content = None
            else:
                text_content = None

            # 如果文件解析失败或不存在,从 chunks 读取
            if not text_content:
                logger.info("reading_from_chunks", document_id=str(document.id))
                from app.models.document_chunk import DocumentChunk

                stmt = (
                    select(DocumentChunk)
                    .where(DocumentChunk.document_id == document.id)
                    .order_by(DocumentChunk.chunk_index)
                )
                result = await self.db.execute(stmt)
                chunks = result.scalars().all()

                if chunks:
                    text_content = "\n\n".join([chunk.content for chunk in chunks])
                    logger.info("chunks_loaded",
                               document_id=str(document.id),
                               chunk_count=len(chunks))
                else:
                    # 如果都没有,使用文档标题作为降级方案
                    logger.warning("no_content_available", document_id=str(document.id))
                    text_content = f"文档标题：{document.title}"

            # 调用 AI 服务生成摘要
            summary_data = await self.ai_service.generate_summary(
                text=text_content, depth=depth
            )

            # 准备摘要内容（JSON格式）
            content = {
                "abstract": summary_data.get("abstract", ""),
                "key_insights": summary_data.get("key_insights", []),
                "main_concepts": summary_data.get("main_concepts", []),
                "depth": depth,
            }

            # 生成纯文本版本
            text_parts = [f"摘要：{summary_data.get('abstract', '')}"]
            if summary_data.get("key_insights"):
                text_parts.append("\n关键见解：")
                for insight in summary_data["key_insights"]:
                    text_parts.append(f"- {insight}")
            if summary_data.get("main_concepts"):
                text_parts.append("\n主要概念：" + "、".join(summary_data["main_concepts"]))
            text_version = "\n".join(text_parts)

            # AI 元数据
            ai_metadata = {
                "model": summary_data.get("model", "qwen-max"),
                "depth": depth,
            }

            # 创建或更新摘要记录
            stmt = select(AISummary).where(AISummary.document_id == document.id)
            result = await self.db.execute(stmt)
            existing_summary = result.scalar_one_or_none()

            if existing_summary:
                # 更新现有摘要
                existing_summary.content = content
                existing_summary.text = text_version
                existing_summary.ai_metadata = ai_metadata
                existing_summary.summary_type = "full"
                summary = existing_summary
            else:
                # 创建新摘要
                from uuid import uuid4
                summary = AISummary(
                    id=str(uuid4()),
                    document_id=document.id,
                    summary_type="full",
                    content=content,
                    text=text_version,
                    ai_metadata=ai_metadata,
                )
                self.db.add(summary)

            await self.db.commit()
            await self.db.refresh(summary)

            # 更新缓存
            cache_key = f"summary:{document.id}"
            await self._safe_cache_set(cache_key, "1", expire=7 * 24 * 3600)

            logger.info(
                "summary_generated_successfully",
                document_id=str(document.id),
                summary_id=str(summary.id),
            )

            return summary

        except Exception as e:
            logger.error(
                "summary_generation_failed",
                document_id=str(document.id),
                error=str(e),
            )
            raise

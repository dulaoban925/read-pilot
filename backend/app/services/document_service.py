"""文档服务"""
import hashlib
import uuid
from pathlib import Path
from typing import List, Optional

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import (
    DocumentProcessingError,
    FileSizeTooLargeError,
    InvalidFileTypeError,
    PageCountExceededError,
)
from app.models.document import Document
from app.models.user import User
from app.utils.file_handler import get_file_storage
from app.utils.logger import get_logger

logger = get_logger(__name__)


class DocumentService:
    """文档服务类"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_document(
        self,
        user: User,
        file: UploadFile,
        title: Optional[str] = None
    ) -> Document:
        """
        创建文档记录

        Args:
            user: 用户对象
            file: 上传的文件
            title: 文档标题（可选，默认使用文件名）

        Returns:
            Document: 创建的文档对象
        """
        # 验证文件类型
        file_ext = Path(file.filename or "").suffix.lower()
        allowed_extensions = settings.ALLOWED_EXTENSIONS
        if file_ext not in allowed_extensions:
            logger.warning("invalid_file_type_upload_attempt", file_type=file_ext)
            raise InvalidFileTypeError(file_ext, list(allowed_extensions))

        # 读取文件内容
        file_content = await file.read()
        file_size = len(file_content)

        # 验证文件大小 (T080)
        max_size = settings.MAX_UPLOAD_SIZE
        if file_size > max_size:
            logger.warning(
                "file_size_exceeded",
                file_size=file_size,
                max_size=max_size,
                file_size_mb=round(file_size / 1024 / 1024, 2),
            )
            raise FileSizeTooLargeError(file_size, max_size)

        # 计算文件hash
        file_hash = hashlib.sha256(file_content).hexdigest()

        # 检查是否已存在
        existing = await self.db.execute(
            select(Document).where(
                Document.user_id == user.id,
                Document.file_hash == file_hash
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("该文档已存在")

        # 生成文档ID和文件路径
        doc_id = str(uuid.uuid4())
        file_path = Path(settings.UPLOAD_DIR) / user.id / f"{doc_id}{file_ext}"
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # 保存文件
        file_path.write_bytes(file_content)

        # 创建文档记录
        document = Document(
            id=doc_id,
            user_id=user.id,
            title=title or file.filename or "Untitled",
            file_path=str(file_path),
            file_hash=file_hash,
            file_size=file_size,
            file_type=file_ext.lstrip('.'),
            processing_status="pending",
            is_indexed=False
        )

        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)

        return document

    async def get_document(
        self,
        document_id: str,
        user: User
    ) -> Optional[Document]:
        """
        获取文档

        Args:
            document_id: 文档ID
            user: 用户对象

        Returns:
            Document or None
        """
        result = await self.db.execute(
            select(Document).where(
                Document.id == document_id,
                Document.user_id == user.id
            )
        )
        return result.scalar_one_or_none()

    async def list_documents(
        self,
        user: User,
        skip: int = 0,
        limit: int = 20,
        status: Optional[str] = None
    ) -> tuple[List[Document], int]:
        """
        列出用户的文档

        Args:
            user: 用户对象
            skip: 跳过数量
            limit: 限制数量
            status: 过滤状态

        Returns:
            (文档列表, 总数)
        """
        query = select(Document).where(Document.user_id == user.id)

        if status:
            query = query.where(Document.processing_status == status)

        # 获取总数
        total_result = await self.db.execute(
            select(Document.id).where(Document.user_id == user.id)
        )
        total = len(total_result.all())

        # 获取文档列表
        query = query.order_by(Document.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        documents = result.scalars().all()

        return list(documents), total

    async def update_document(
        self,
        document_id: str,
        user: User,
        title: Optional[str] = None,
        processing_status: Optional[str] = None,
        processing_error: Optional[str] = None,
        page_count: Optional[int] = None,
        word_count: Optional[int] = None,
        is_indexed: Optional[bool] = None
    ) -> Optional[Document]:
        """
        更新文档

        Args:
            document_id: 文档ID
            user: 用户对象
            title: 新标题
            processing_status: 处理状态
            processing_error: 处理错误
            page_count: 页数
            word_count: 字数
            is_indexed: 是否已索引

        Returns:
            Document or None
        """
        document = await self.get_document(document_id, user)
        if not document:
            return None

        if title is not None:
            document.title = title
        if processing_status is not None:
            document.processing_status = processing_status
        if processing_error is not None:
            document.processing_error = processing_error
        if page_count is not None:
            document.page_count = page_count
        if word_count is not None:
            document.word_count = word_count
        if is_indexed is not None:
            document.is_indexed = is_indexed

        await self.db.commit()
        await self.db.refresh(document)

        return document

    async def delete_document(
        self,
        document_id: str,
        user: User
    ) -> bool:
        """
        删除文档

        Args:
            document_id: 文档ID
            user: 用户对象

        Returns:
            bool: 是否删除成功
        """
        document = await self.get_document(document_id, user)
        if not document:
            return False

        # 删除文件
        try:
            file_path = Path(document.file_path)
            if file_path.exists():
                file_path.unlink()
        except Exception as e:
            print(f"删除文件失败: {e}")

        # 删除数据库记录
        await self.db.delete(document)
        await self.db.commit()

        return True

    async def get_document_file(self, document: Document) -> bytes:
        """
        获取文档文件内容 (T068)

        Args:
            document: 文档对象

        Returns:
            文件内容字节

        Raises:
            DocumentProcessingError: 文件读取失败
        """
        try:
            file_storage = get_file_storage()
            # 从文件路径提取相对路径
            # file_path 格式: user_id/document_id.ext
            relative_path = Path(document.file_path).name
            full_relative_path = f"{document.user_id}/{relative_path}"

            file_content = await file_storage.get(full_relative_path)
            logger.info(
                "document_file_retrieved",
                document_id=str(document.id),
                file_size=len(file_content),
            )
            return file_content

        except Exception as e:
            logger.error(
                "document_file_retrieval_failed",
                document_id=str(document.id),
                error=str(e),
            )
            raise DocumentProcessingError(
                str(document.id), f"无法读取文件: {str(e)}"
            )

    def validate_page_count(self, page_count: int) -> None:
        """
        验证文档页数 (T080)

        Args:
            page_count: 页数

        Raises:
            PageCountExceededError: 页数超过限制
        """
        max_pages = settings.MAX_DOCUMENT_PAGES if hasattr(settings, "MAX_DOCUMENT_PAGES") else 1000
        if page_count > max_pages:
            logger.warning(
                "page_count_exceeded",
                page_count=page_count,
                max_pages=max_pages,
            )
            raise PageCountExceededError(page_count, max_pages)

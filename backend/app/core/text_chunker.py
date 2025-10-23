"""文本分块服务"""
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.config import settings


class TextChunker:
    """文本分块器，用于将文档分割成适合向量化的块"""

    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None
    ):
        """
        初始化文本分块器

        Args:
            chunk_size: 块大小(token数)，默认使用配置
            chunk_overlap: 块重叠大小(token数)，默认使用配置
        """
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

        # 使用LangChain的RecursiveCharacterTextSplitter
        # 估算: 1 token ≈ 4 characters (对英文)
        char_chunk_size = self.chunk_size * 4
        char_chunk_overlap = self.chunk_overlap * 4

        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=char_chunk_size,
            chunk_overlap=char_chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", "。", "！", "？", ". ", "! ", "? ", " ", ""],
        )

    def chunk_text(self, text: str) -> List[str]:
        """
        将文本分割成块

        Args:
            text: 要分割的文本

        Returns:
            List[str]: 文本块列表
        """
        if not text or not text.strip():
            return []

        chunks = self.splitter.split_text(text)
        return chunks

    def chunk_with_metadata(
        self,
        text: str,
        metadata: dict | None = None
    ) -> List[dict]:
        """
        将文本分割成块，并附带元数据

        Args:
            text: 要分割的文本
            metadata: 附加的元数据

        Returns:
            List[dict]: 包含文本和元数据的块列表
        """
        chunks = self.chunk_text(text)
        metadata = metadata or {}

        result = []
        for idx, chunk in enumerate(chunks):
            chunk_data = {
                "content": chunk,
                "chunk_index": idx,
                "token_count": self._estimate_tokens(chunk),
                "metadata": {**metadata, "chunk_index": idx}
            }
            result.append(chunk_data)

        return result

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """
        估算文本的token数

        Args:
            text: 文本

        Returns:
            int: 估算的token数
        """
        # 简单估算: 1 token ≈ 4 characters (对英文)
        # 对中文: 1 token ≈ 1.5 characters
        # 这里使用保守估算
        return len(text) // 3


# 创建全局分块器实例
text_chunker = TextChunker()


__all__ = ["TextChunker", "text_chunker"]

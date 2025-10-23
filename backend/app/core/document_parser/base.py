"""文档解析器基类"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional


class ParsedDocument:
    """解析后的文档数据结构"""

    def __init__(
        self,
        text: str,
        metadata: Optional[Dict] = None,
        pages: Optional[List[str]] = None
    ):
        self.text = text
        self.metadata = metadata or {}
        self.pages = pages or []

    @property
    def word_count(self) -> int:
        """获取文档字数"""
        return len(self.text.split())

    @property
    def page_count(self) -> int:
        """获取页数"""
        return len(self.pages) if self.pages else None


class BaseDocumentParser(ABC):
    """文档解析器抽象基类"""

    @abstractmethod
    async def parse(self, file_path: Path) -> ParsedDocument:
        """
        解析文档

        Args:
            file_path: 文件路径

        Returns:
            ParsedDocument: 解析后的文档

        Raises:
            ValueError: 文件格式不支持或解析失败
        """
        pass

    @abstractmethod
    def supports(self, file_extension: str) -> bool:
        """
        检查是否支持指定的文件扩展名

        Args:
            file_extension: 文件扩展名 (如 '.pdf')

        Returns:
            bool: 是否支持
        """
        pass

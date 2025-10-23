"""EPUB文档解析器"""
from pathlib import Path
from typing import List

import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup

from app.core.document_parser.base import BaseDocumentParser, ParsedDocument


class EPUBParser(BaseDocumentParser):
    """EPUB文档解析器"""

    def supports(self, file_extension: str) -> bool:
        """支持.epub文件"""
        return file_extension.lower() == ".epub"

    async def parse(self, file_path: Path) -> ParsedDocument:
        """
        解析EPUB文档

        Args:
            file_path: EPUB文件路径

        Returns:
            ParsedDocument: 解析后的文档

        Raises:
            ValueError: EPUB解析失败
        """
        try:
            book = epub.read_epub(str(file_path))

            # 提取文本
            chapters: List[str] = []

            for item in book.get_items():
                if item.get_type() == ebooklib.ITEM_DOCUMENT:
                    # 解析HTML内容
                    soup = BeautifulSoup(item.get_content(), "html.parser")
                    text = soup.get_text(separator="\n", strip=True)
                    if text:
                        chapters.append(text)

            full_text = "\n\n".join(chapters)

            # 提取元数据
            metadata = {
                "format": "epub",
                "chapter_count": len(chapters),
            }

            # 添加EPUB元数据
            if book.get_metadata("DC", "title"):
                metadata["title"] = book.get_metadata("DC", "title")[0][0]
            if book.get_metadata("DC", "creator"):
                metadata["author"] = book.get_metadata("DC", "creator")[0][0]
            if book.get_metadata("DC", "language"):
                metadata["language"] = book.get_metadata("DC", "language")[0][0]
            if book.get_metadata("DC", "publisher"):
                metadata["publisher"] = book.get_metadata("DC", "publisher")[0][0]

            return ParsedDocument(
                text=full_text,
                metadata=metadata,
                pages=chapters  # 使用章节作为"页面"
            )

        except Exception as e:
            raise ValueError(f"Failed to parse EPUB: {str(e)}")

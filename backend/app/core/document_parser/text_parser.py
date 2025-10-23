"""文本和Markdown文档解析器"""
from pathlib import Path

import markdown

from app.core.document_parser.base import BaseDocumentParser, ParsedDocument


class TextParser(BaseDocumentParser):
    """纯文本文档解析器"""

    def supports(self, file_extension: str) -> bool:
        """支持.txt文件"""
        return file_extension.lower() == ".txt"

    async def parse(self, file_path: Path) -> ParsedDocument:
        """
        解析文本文档

        Args:
            file_path: 文本文件路径

        Returns:
            ParsedDocument: 解析后的文档

        Raises:
            ValueError: 文本解析失败
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()

            metadata = {
                "format": "txt",
            }

            return ParsedDocument(
                text=text,
                metadata=metadata
            )

        except Exception as e:
            raise ValueError(f"Failed to parse text file: {str(e)}")


class MarkdownParser(BaseDocumentParser):
    """Markdown文档解析器"""

    def supports(self, file_extension: str) -> bool:
        """支持.md和.markdown文件"""
        return file_extension.lower() in [".md", ".markdown"]

    async def parse(self, file_path: Path) -> ParsedDocument:
        """
        解析Markdown文档

        Args:
            file_path: Markdown文件路径

        Returns:
            ParsedDocument: 解析后的文档

        Raises:
            ValueError: Markdown解析失败
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                md_text = f.read()

            # 保留原始Markdown文本用于向量化
            # 也可以转换为HTML再提取纯文本，但原始格式通常更好
            text = md_text

            metadata = {
                "format": "markdown",
            }

            return ParsedDocument(
                text=text,
                metadata=metadata
            )

        except Exception as e:
            raise ValueError(f"Failed to parse Markdown file: {str(e)}")

"""PDF文档解析器"""
from pathlib import Path
from typing import Dict, List

import pymupdf

from app.core.document_parser.base import BaseDocumentParser, ParsedDocument


class PDFParser(BaseDocumentParser):
    """PDF文档解析器 (使用PyMuPDF)"""

    def supports(self, file_extension: str) -> bool:
        """支持.pdf文件"""
        return file_extension.lower() == ".pdf"

    async def parse(self, file_path: Path) -> ParsedDocument:
        """
        解析PDF文档

        Args:
            file_path: PDF文件路径

        Returns:
            ParsedDocument: 解析后的文档

        Raises:
            ValueError: PDF解析失败
        """
        try:
            doc = pymupdf.open(file_path)

            # 提取文本和页面
            pages: List[str] = []
            full_text_parts: List[str] = []

            for page_num in range(len(doc)):
                page = doc[page_num]
                page_text = page.get_text()
                pages.append(page_text)
                full_text_parts.append(page_text)

            full_text = "\n\n".join(full_text_parts)

            # 提取元数据
            metadata: Dict = {
                "page_count": len(doc),
                "format": "pdf",
            }

            # 添加PDF元数据
            pdf_metadata = doc.metadata
            if pdf_metadata:
                if pdf_metadata.get("title"):
                    metadata["title"] = pdf_metadata["title"]
                if pdf_metadata.get("author"):
                    metadata["author"] = pdf_metadata["author"]
                if pdf_metadata.get("subject"):
                    metadata["subject"] = pdf_metadata["subject"]
                if pdf_metadata.get("creator"):
                    metadata["creator"] = pdf_metadata["creator"]

            doc.close()

            return ParsedDocument(
                text=full_text,
                metadata=metadata,
                pages=pages
            )

        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {str(e)}")

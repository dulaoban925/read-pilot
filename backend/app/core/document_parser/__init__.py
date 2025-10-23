"""Document parser module"""
from pathlib import Path
from typing import List

from app.core.document_parser.base import BaseDocumentParser, ParsedDocument
from app.core.document_parser.docx_parser import DOCXParser
from app.core.document_parser.epub_parser import EPUBParser
from app.core.document_parser.pdf_parser import PDFParser
from app.core.document_parser.text_parser import MarkdownParser, TextParser


class DocumentParserFactory:
    """Document parser factory"""

    def __init__(self):
        self.parsers: List[BaseDocumentParser] = [
            PDFParser(),
            EPUBParser(),
            DOCXParser(),
            TextParser(),
            MarkdownParser(),
        ]

    def get_parser(self, file_path: Path) -> BaseDocumentParser:
        """
        Get parser by file extension

        Args:
            file_path: File path

        Returns:
            BaseDocumentParser: Corresponding parser

        Raises:
            ValueError: Unsupported file type
        """
        file_extension = file_path.suffix.lower()

        for parser in self.parsers:
            if parser.supports(file_extension):
                return parser

        raise ValueError(f"Unsupported file type: {file_extension}")

    async def parse_document(self, file_path: Path) -> ParsedDocument:
        """
        Parse document

        Args:
            file_path: File path

        Returns:
            ParsedDocument: Parsed document

        Raises:
            ValueError: Unsupported file type or parse failure
        """
        parser = self.get_parser(file_path)
        return await parser.parse(file_path)


# Create global factory instance
document_parser_factory = DocumentParserFactory()


__all__ = [
    "BaseDocumentParser",
    "ParsedDocument",
    "PDFParser",
    "EPUBParser",
    "DOCXParser",
    "TextParser",
    "MarkdownParser",
    "DocumentParserFactory",
    "document_parser_factory",
]

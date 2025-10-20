"""
Document processing tools
"""
from parlant import tool, ToolContext, ToolResult
from typing import Optional, List, Dict
import PyPDF2
import docx
import re


@tool
async def extract_text(
    context: ToolContext,
    document_id: str,
    page_range: Optional[tuple[int, int]] = None
) -> ToolResult:
    """
    Extract text from a document

    Args:
        context: Parlant tool context
        document_id: Document identifier
        page_range: Optional tuple of (start_page, end_page)

    Returns:
        Extracted text content
    """
    # TODO: Implement actual document retrieval from storage
    # This is a placeholder implementation

    try:
        # Get document from database/storage
        document_path = f"/storage/documents/{document_id}"

        # Detect file type and extract accordingly
        if document_path.endswith('.pdf'):
            text = _extract_from_pdf(document_path, page_range)
        elif document_path.endswith('.docx'):
            text = _extract_from_docx(document_path)
        elif document_path.endswith(('.txt', '.md')):
            with open(document_path, 'r', encoding='utf-8') as f:
                text = f.read()
        else:
            return ToolResult(
                success=False,
                message=f"Unsupported file type for document {document_id}"
            )

        # Store extracted text in context for later use
        context.variables["current_document_text"] = text
        context.variables["current_document_id"] = document_id

        return ToolResult(
            success=True,
            data={"text": text, "length": len(text)}
        )

    except Exception as e:
        return ToolResult(
            success=False,
            message=f"Failed to extract text: {str(e)}"
        )


def _extract_from_pdf(file_path: str, page_range: Optional[tuple[int, int]] = None) -> str:
    """Extract text from PDF file"""
    text = []
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        total_pages = len(pdf_reader.pages)

        start_page = page_range[0] if page_range else 0
        end_page = page_range[1] if page_range else total_pages

        for page_num in range(start_page, min(end_page, total_pages)):
            page = pdf_reader.pages[page_num]
            text.append(page.extract_text())

    return "\n".join(text)


def _extract_from_docx(file_path: str) -> str:
    """Extract text from DOCX file"""
    doc = docx.Document(file_path)
    return "\n".join([paragraph.text for paragraph in doc.paragraphs])


@tool
async def detect_document_type(
    context: ToolContext,
    text: Optional[str] = None
) -> ToolResult:
    """
    Detect document type (technical, narrative, academic, news)

    Args:
        context: Parlant tool context
        text: Optional text to analyze (uses context if not provided)

    Returns:
        Detected document type
    """
    if text is None:
        text = context.variables.get("current_document_text", "")

    if not text:
        return ToolResult(
            success=False,
            message="No text provided for document type detection"
        )

    # Simple heuristic-based detection (can be replaced with ML model)
    text_lower = text.lower()

    # Keywords for different document types
    technical_keywords = [
        'algorithm', 'implementation', 'system', 'architecture',
        'method', 'function', 'class', 'variable', 'code'
    ]
    academic_keywords = [
        'abstract', 'introduction', 'methodology', 'results',
        'conclusion', 'references', 'hypothesis', 'research'
    ]
    narrative_keywords = [
        'story', 'character', 'plot', 'scene', 'chapter',
        'narrative', 'once upon', 'he said', 'she said'
    ]

    # Count keyword occurrences
    technical_score = sum(1 for kw in technical_keywords if kw in text_lower)
    academic_score = sum(1 for kw in academic_keywords if kw in text_lower)
    narrative_score = sum(1 for kw in narrative_keywords if kw in text_lower)

    # Determine document type
    scores = {
        'technical': technical_score,
        'academic': academic_score,
        'narrative': narrative_score,
        'news': 0  # Default fallback
    }

    document_type = max(scores, key=scores.get)
    if scores[document_type] == 0:
        document_type = 'general'

    # Store in context
    context.variables["document_type"] = document_type

    return ToolResult(
        success=True,
        data={
            "document_type": document_type,
            "confidence_scores": scores
        }
    )


@tool
async def retrieve_document_context(
    context: ToolContext,
    document_id: str
) -> ToolResult:
    """
    Retrieve document metadata and context

    Args:
        context: Parlant tool context
        document_id: Document identifier

    Returns:
        Document metadata and context
    """
    # TODO: Implement actual database query
    # This is a placeholder implementation

    document_context = {
        "document_id": document_id,
        "title": context.variables.get("document_title", "Untitled"),
        "type": context.variables.get("document_type", "general"),
        "page_count": context.variables.get("page_count", 0),
        "summary": context.variables.get("last_summary", {}),
    }

    return ToolResult(
        success=True,
        data=document_context
    )


@tool
async def cite_source(
    context: ToolContext,
    answer: str,
    passages: List[Dict]
) -> ToolResult:
    """
    Add source citations to an answer

    Args:
        context: Parlant tool context
        answer: The answer text
        passages: List of passage dictionaries with 'text' and 'page' keys

    Returns:
        Answer with citations
    """
    if not passages:
        return ToolResult(
            success=True,
            data={"cited_answer": answer}
        )

    # Build citations
    citations = []
    for i, passage in enumerate(passages, 1):
        page = passage.get('page', 'unknown')
        text_preview = passage.get('text', '')[:100] + "..."
        citations.append(f"[{i}] 第 {page} 页: {text_preview}")

    cited_answer = f"{answer}\n\n📚 参考来源:\n" + "\n".join(citations)

    return ToolResult(
        success=True,
        data={"cited_answer": cited_answer}
    )

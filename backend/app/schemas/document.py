"""文档Schemas"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class DocumentBase(BaseModel):
    """文档基础schema"""
    title: str = Field(..., min_length=1, max_length=500)
    file_type: str = Field(..., pattern="^(pdf|epub|docx|txt|md)$")


class DocumentCreate(DocumentBase):
    """文档创建schema"""
    pass


class DocumentUpdate(BaseModel):
    """文档更新schema"""
    title: Optional[str] = Field(None, min_length=1, max_length=500)


class DocumentResponse(DocumentBase):
    """文档响应schema"""
    id: str
    user_id: str
    file_path: str
    file_hash: str
    file_size: int
    author: Optional[str] = None
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    processing_status: str  # pending, processing, completed, failed
    processing_error: Optional[str] = None
    is_indexed: bool
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class DocumentListData(BaseModel):
    """文档列表数据schema"""
    items: List[DocumentResponse]
    total: int
    page: int = 1
    page_size: int = 20
    total_pages: int = 0


class DocumentChunkBase(BaseModel):
    """文档块基础schema"""
    content: str
    token_count: int
    chunk_index: int


class DocumentChunkResponse(DocumentChunkBase):
    """文档块响应schema"""
    id: str
    document_id: str
    start_char: Optional[int] = None
    end_char: Optional[int] = None
    location_metadata: Optional[dict] = None
    embedding_id: Optional[str] = None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }


class SummaryCreate(BaseModel):
    """摘要创建请求 schema"""
    depth_level: str = Field(default="detailed", pattern="^(brief|detailed)$")


class SummaryResponse(BaseModel):
    """摘要响应 schema"""
    id: str
    document_id: str
    abstract: str = Field(..., description="摘要概述")
    key_insights: List[str] = Field(..., description="关键见解列表")
    main_concepts: List[str] = Field(..., description="主要概念列表")
    depth_level: str = Field(..., description="摘要深度")
    model_used: str = Field(..., description="使用的 AI 模型")
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }

    @classmethod
    def from_ai_summary(cls, summary: 'AISummary') -> 'SummaryResponse':
        """从 AISummary 模型创建响应对象"""
        content = summary.content or {}
        ai_metadata = summary.ai_metadata or {}

        return cls(
            id=summary.id,
            document_id=summary.document_id,
            abstract=content.get('abstract', ''),
            key_insights=content.get('key_insights', []),
            main_concepts=content.get('main_concepts', []),
            depth_level=content.get('depth', 'detailed'),
            model_used=ai_metadata.get('model', 'unknown'),
            created_at=summary.created_at,
            updated_at=summary.updated_at,
        )

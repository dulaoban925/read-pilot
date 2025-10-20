"""
Document model and related schemas
"""
from sqlalchemy import Column, String, Integer, DateTime, JSON, Text, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List, Dict

Base = declarative_base()


class Document(Base):
    """Document database model"""

    __tablename__ = "documents"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)

    # Document metadata
    title = Column(String, nullable=False)
    file_name = Column(String, nullable=False)
    file_type = Column(String, nullable=False)  # pdf, txt, md, docx
    file_size = Column(Integer, nullable=False)  # in bytes
    file_path = Column(String, nullable=False)  # storage path

    # Document analysis
    document_type = Column(String, nullable=True)  # technical, narrative, academic, news
    page_count = Column(Integer, default=0)
    word_count = Column(Integer, default=0)
    language = Column(String, default="zh")

    # Summary (stored as JSON)
    summary = Column(JSON, nullable=True)

    # Status
    processing_status = Column(String, default="pending")  # pending, processing, completed, failed
    indexed = Column(Integer, default=0)  # 0 = not indexed, 1 = indexed

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DocumentChunk(Base):
    """Document chunk for vector embedding"""

    __tablename__ = "document_chunks"

    id = Column(String, primary_key=True)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False, index=True)

    # Chunk content
    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)

    # Vector embedding
    embedding_vector = Column(JSON, nullable=True)  # Store as JSON array

    # Metadata (renamed to avoid SQLAlchemy reserved word)
    chunk_metadata = Column(JSON, default={})

    created_at = Column(DateTime, default=datetime.utcnow)


# Pydantic schemas for API

class DocumentCreate(BaseModel):
    """Schema for creating a document"""
    title: str
    file_name: str
    file_type: str
    user_id: str


class DocumentUpdate(BaseModel):
    """Schema for updating document"""
    title: Optional[str] = None
    document_type: Optional[str] = None
    summary: Optional[Dict] = None


class DocumentResponse(BaseModel):
    """Schema for document response"""
    id: str
    user_id: str
    title: str
    file_name: str
    file_type: str
    file_size: int
    document_type: Optional[str] = None
    page_count: int
    word_count: int
    language: str
    summary: Optional[Dict] = None
    processing_status: str
    indexed: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class DocumentSummaryResponse(BaseModel):
    """Schema for document summary"""
    document_id: str
    abstract: str
    key_insights: List[str]
    concepts: Dict[str, str]
    examples: List[str]


class DocumentChunkCreate(BaseModel):
    """Schema for creating document chunk"""
    document_id: str
    chunk_index: int
    text: str
    page_number: Optional[int] = None
    chunk_metadata: Optional[Dict] = None


class DocumentChunkResponse(BaseModel):
    """Schema for document chunk response"""
    id: str
    document_id: str
    chunk_index: int
    text: str
    page_number: Optional[int] = None
    chunk_metadata: Dict

    class Config:
        from_attributes = True

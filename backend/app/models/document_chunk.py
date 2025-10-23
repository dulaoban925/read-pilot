"""Document Chunk Model"""
from typing import Optional

from sqlalchemy import Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class DocumentChunk(Base, TimestampMixin):
    """Document chunk model for RAG and vector search"""

    __tablename__ = "document_chunks"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    document_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Chunk content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False)

    # Position in document
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    start_char: Mapped[Optional[int]] = mapped_column(Integer)
    end_char: Mapped[Optional[int]] = mapped_column(Integer)

    # Location metadata (JSON)
    # Example: {"page": 5, "chapter": "Introduction", "section": "Overview"}
    location_metadata: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)

    # Vector embedding metadata
    embedding_id: Mapped[Optional[str]] = mapped_column(String(100))  # ChromaDB ID
    embedding_model: Mapped[Optional[str]] = mapped_column(String(100))  # e.g., "text-embedding-3-small"

    # Semantic score (used for ranking/filtering)
    semantic_score: Mapped[Optional[float]] = mapped_column(Float)

    # Relationships
    document = relationship("Document", back_populates="chunks")

    def __repr__(self) -> str:
        return f"<DocumentChunk(id={self.id}, chunk_index={self.chunk_index}, tokens={self.token_count})>"

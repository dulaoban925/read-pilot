"""Document Model"""
from datetime import datetime
from typing import Optional

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Document(Base, TimestampMixin):
    """Document model"""

    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(50), ForeignKey("users.id"), nullable=False, index=True)

    # File information
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), nullable=False, index=True)  # SHA-256 hash
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)  # in bytes
    file_type: Mapped[str] = mapped_column(String(50), nullable=False)  # pdf, epub, txt, md, docx

    # Document metadata
    author: Mapped[Optional[str]] = mapped_column(String(255))
    page_count: Mapped[Optional[int]] = mapped_column(Integer)
    word_count: Mapped[Optional[int]] = mapped_column(Integer)

    # Parsed content (JSON structure)
    parsed_content: Mapped[Optional[dict]] = mapped_column(JSON)

    # Processing status
    processing_status: Mapped[str] = mapped_column(
        String(20),
        default="pending",
        nullable=False
    )  # pending, processing, completed, failed
    processing_error: Mapped[Optional[str]] = mapped_column(Text)

    # Reading progress
    current_page: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    scroll_position: Mapped[Optional[float]] = mapped_column()  # 0.0 to 1.0
    last_read_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Vector embedding status
    is_indexed: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Relationships
    user = relationship("User", back_populates="documents")
    annotations = relationship("Annotation", back_populates="document", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="document", cascade="all, delete-orphan")
    reading_sessions = relationship("ReadingSession", back_populates="document", cascade="all, delete-orphan")
    ai_summaries = relationship("AISummary", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Document(id={self.id}, title={self.title})>"

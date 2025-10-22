"""Annotation Model"""
from typing import Optional

from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Annotation(Base, TimestampMixin):
    """Annotation model for highlights, notes, and bookmarks"""

    __tablename__ = "annotations"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(50), ForeignKey("users.id"), nullable=False, index=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("documents.id"), nullable=False, index=True)

    # Annotation type: highlight, important, note, bookmark
    type: Mapped[str] = mapped_column(String(20), nullable=False)

    # Position in document (JSON structure)
    # Example: {"page": 5, "start": 100, "end": 200, "bbox": {...}}
    position: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Selected text
    selected_text: Mapped[str] = mapped_column(Text, nullable=False)

    # User's note/comment (for type='note')
    note_content: Mapped[Optional[str]] = mapped_column(Text)

    # Color for highlights (yellow, red, green, blue)
    color: Mapped[str] = mapped_column(String(20), default="yellow", nullable=False)

    # Tags (JSON array)
    tags: Mapped[Optional[list]] = mapped_column(JSON, default=list)

    # Relationships
    user = relationship("User", back_populates="annotations")
    document = relationship("Document", back_populates="annotations")

    def __repr__(self) -> str:
        return f"<Annotation(id={self.id}, type={self.type})>"

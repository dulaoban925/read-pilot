"""AI Summary Model"""
from typing import Optional

from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class AISummary(Base, TimestampMixin):
    """AI-generated summary model"""

    __tablename__ = "ai_summaries"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("documents.id"), nullable=False, index=True)

    # Summary type: full, chapter, section, custom
    summary_type: Mapped[str] = mapped_column(String(20), nullable=False)

    # Summary content structure (JSON)
    # Example: {
    #   "topic": "...",
    #   "core_points": [...],
    #   "conclusions": [...],
    #   "highlights": [...]
    # }
    content: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Plain text version
    text: Mapped[str] = mapped_column(Text, nullable=False)

    # AI metadata (JSON)
    # Example: {"model": "gpt-4", "tokens": 500, "cost": 0.01}
    metadata: Mapped[Optional[dict]] = mapped_column(JSON)

    # Target section (for chapter/section summaries)
    target_section: Mapped[Optional[str]] = mapped_column(String(255))

    # Guiding questions generated with summary (JSON array)
    guiding_questions: Mapped[Optional[list]] = mapped_column(JSON, default=list)

    # Relationships
    document = relationship("Document", back_populates="ai_summaries")

    def __repr__(self) -> str:
        return f"<AISummary(id={self.id}, type={self.summary_type})>"

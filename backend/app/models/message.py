"""Message Model"""
from typing import Optional

from sqlalchemy import Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class Message(Base, TimestampMixin):
    """Message model for chat sessions"""

    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    session_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Message role: user, assistant, system
    role: Mapped[str] = mapped_column(String(20), nullable=False)

    # Message content
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Token usage
    token_count: Mapped[Optional[int]] = mapped_column(Integer)

    # AI model used (for assistant messages)
    model: Mapped[Optional[str]] = mapped_column(String(100))

    # Source citations (JSON array)
    # Example: [{"chunk_id": "...", "text": "...", "page": 5, "relevance": 0.95}]
    sources: Mapped[Optional[list]] = mapped_column(JSON, default=list)

    # Confidence score (for AI responses)
    confidence: Mapped[Optional[float]] = mapped_column(Float)

    # Response metadata (JSON)
    # Example: {"latency_ms": 1500, "provider": "openai", "cost": 0.002}
    response_metadata: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)

    # Feedback from user
    feedback: Mapped[Optional[str]] = mapped_column(String(20))  # helpful, not_helpful, incorrect

    # Relationships
    session = relationship("ChatSession", back_populates="messages")

    def __repr__(self) -> str:
        return f"<Message(id={self.id}, role={self.role}, session_id={self.session_id})>"

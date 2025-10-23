"""Chat Message Model"""
from typing import Optional

from sqlalchemy import Enum, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class ChatMessage(Base, TimestampMixin):
    """Chat message model for Q&A interactions"""

    __tablename__ = "chat_messages"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(50), ForeignKey("users.id"), nullable=False, index=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("documents.id"), nullable=False, index=True)

    # Message role: user or assistant
    role: Mapped[str] = mapped_column(
        Enum("user", "assistant", name="message_role"),
        nullable=False
    )

    # Message content
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # AI response metadata (for role='assistant')
    # Example: {"model": "gpt-4", "tokens": 150, "sources": [...]}
    message_metadata: Mapped[Optional[dict]] = mapped_column(JSON)

    # Source references for AI answers (JSON array)
    # Example: [{"text": "...", "page": 5, "position": {...}}, ...]
    sources: Mapped[Optional[list]] = mapped_column(JSON, default=list)

    # Parent message ID (for threading)
    parent_id: Mapped[Optional[str]] = mapped_column(String(50), ForeignKey("chat_messages.id"))

    # Relationships
    user = relationship("User", back_populates="chat_messages")
    document = relationship("Document", back_populates="chat_messages")

    def __repr__(self) -> str:
        return f"<ChatMessage(id={self.id}, role={self.role})>"

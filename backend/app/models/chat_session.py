"""Chat Session Model"""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class ChatSession(Base, TimestampMixin):
    """Chat session model for grouping conversations"""

    __tablename__ = "chat_sessions"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    user_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    document_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Session metadata
    title: Mapped[str] = mapped_column(String(500), nullable=False, default="New Chat")
    message_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Session timing
    last_message_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Session context settings (JSON)
    # Example: {"temperature": 0.7, "max_tokens": 500, "context_window": 10}
    settings: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)

    # Session summary (auto-generated for long chats)
    summary: Mapped[Optional[str]] = mapped_column(String(1000))

    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    document = relationship("Document", back_populates="chat_sessions")
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<ChatSession(id={self.id}, title={self.title}, messages={self.message_count})>"

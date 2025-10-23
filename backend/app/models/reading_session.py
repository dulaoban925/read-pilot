"""Reading Session Model"""
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class ReadingSession(Base, TimestampMixin):
    """Reading session model for tracking user reading behavior"""

    __tablename__ = "reading_sessions"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(50), ForeignKey("users.id"), nullable=False, index=True)
    document_id: Mapped[str] = mapped_column(String(50), ForeignKey("documents.id"), nullable=False, index=True)

    # Session timing
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    duration_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Pages/sections read (JSON array)
    # Example: [1, 2, 3, 5, 7]
    pages_read: Mapped[Optional[list]] = mapped_column(JSON, default=list)

    # Reading statistics
    scroll_events: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    annotations_made: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    questions_asked: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # Session metadata (JSON)
    # Example: {"device": "desktop", "browser": "chrome"}
    session_metadata: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)

    # Relationships
    user = relationship("User", back_populates="reading_sessions")
    document = relationship("Document", back_populates="reading_sessions")

    def __repr__(self) -> str:
        return f"<ReadingSession(id={self.id}, user_id={self.user_id})>"

"""
Session and message models
"""
from sqlalchemy import Column, String, DateTime, JSON, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List, Dict

Base = declarative_base()


class Session(Base):
    """Conversation session model"""

    __tablename__ = "sessions"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    document_id = Column(String, ForeignKey("documents.id"), nullable=True, index=True)

    # Session metadata
    title = Column(String, nullable=True)
    session_type = Column(String, default="chat")  # chat, summarization, quiz, note

    # Context state (stored as JSON)
    context_variables = Column(JSON, default={})

    # Session status
    status = Column(String, default="active")  # active, archived, deleted

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_message_at = Column(DateTime, nullable=True)


class Message(Base):
    """Conversation message model"""

    __tablename__ = "messages"

    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("sessions.id"), nullable=False, index=True)

    # Message content
    role = Column(String, nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)

    # Agent information
    agent_name = Column(String, nullable=True)  # Which agent generated this message

    # Metadata (renamed to avoid SQLAlchemy reserved word)
    message_metadata = Column(JSON, default={})

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)


# Pydantic schemas for API

class SessionCreate(BaseModel):
    """Schema for creating a session"""
    user_id: str
    document_id: Optional[str] = None
    title: Optional[str] = None
    session_type: str = "chat"


class SessionUpdate(BaseModel):
    """Schema for updating session"""
    title: Optional[str] = None
    status: Optional[str] = None
    context_variables: Optional[Dict] = None


class SessionResponse(BaseModel):
    """Schema for session response"""
    id: str
    user_id: str
    document_id: Optional[str] = None
    title: Optional[str] = None
    session_type: str
    status: str
    created_at: datetime
    updated_at: datetime
    last_message_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    """Schema for creating a message"""
    session_id: str
    role: str
    content: str
    agent_name: Optional[str] = None
    message_metadata: Optional[Dict] = None


class MessageResponse(BaseModel):
    """Schema for message response"""
    id: str
    session_id: str
    role: str
    content: str
    agent_name: Optional[str] = None
    message_metadata: Dict
    created_at: datetime

    class Config:
        from_attributes = True


class ChatRequest(BaseModel):
    """Schema for chat request"""
    user_id: str
    message: str
    document_id: Optional[str] = None
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    """Schema for chat response"""
    session_id: str
    message: str
    agent_name: Optional[str] = None
    metadata: Optional[Dict] = None

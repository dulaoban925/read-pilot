"""
User model and related schemas
"""
from sqlalchemy import Column, String, Integer, DateTime, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict

Base = declarative_base()


class User(Base):
    """User database model"""

    __tablename__ = "users"

    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)

    # Preferences (stored as JSON)
    preferences = Column(JSON, default={})

    # Learning statistics
    reading_count = Column(Integer, default=0)
    total_questions_asked = Column(Integer, default=0)
    quiz_scores = Column(JSON, default=[])
    weak_topics = Column(JSON, default=[])
    mastered_topics = Column(JSON, default=[])

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)


# Pydantic schemas for API

class UserPreferences(BaseModel):
    """User preferences schema"""
    summary_style: str = "concise"  # concise, detailed, visual
    difficulty_preference: str = "medium"  # beginner, intermediate, advanced
    language: str = "zh"  # zh, en
    notification_enabled: bool = True


class UserLearningStats(BaseModel):
    """User learning statistics schema"""
    reading_count: int = 0
    total_questions_asked: int = 0
    quiz_scores: List[Dict] = []
    weak_topics: List[str] = []
    mastered_topics: List[str] = []


class UserCreate(BaseModel):
    """Schema for creating a new user"""
    email: EmailStr
    name: str
    password: str


class UserUpdate(BaseModel):
    """Schema for updating user information"""
    name: Optional[str] = None
    preferences: Optional[UserPreferences] = None


class UserResponse(BaseModel):
    """Schema for user response"""
    id: str
    email: str
    name: str
    preferences: UserPreferences
    learning_stats: UserLearningStats
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str

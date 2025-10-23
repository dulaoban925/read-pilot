"""User Schemas"""
from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)


class UserCreate(UserBase):
    """User creation schema"""
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    """User update schema"""
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    preferences: Optional[Dict] = None


class UserResponse(UserBase):
    """User response schema"""
    id: str
    is_active: bool
    is_verified: bool
    preferences: Dict
    total_reading_time: int
    documents_read: int
    questions_asked: int
    notes_created: int
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }


class UserProfileStats(BaseModel):
    """User profile statistics schema"""
    total_reading_time: int = Field(..., description="Total reading time in seconds")
    documents_read: int = Field(..., description="Number of documents read")
    questions_asked: int = Field(..., description="Number of questions asked")
    notes_created: int = Field(..., description="Number of notes/annotations created")
    total_documents: int = Field(..., description="Total number of uploaded documents")
    active_reading_sessions: int = Field(..., description="Number of active reading sessions")

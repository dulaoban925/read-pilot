"""
API routes for ReadPilot
"""
from .chat import router as chat_router
from .documents import router as documents_router
from .users import router as users_router

__all__ = [
    "chat_router",
    "documents_router",
    "users_router",
]

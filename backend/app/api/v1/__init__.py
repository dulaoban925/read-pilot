"""API v1 router"""
from fastapi import APIRouter

from app.api.v1 import auth, documents

api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(documents.router, prefix="/documents", tags=["Documents"])

__all__ = ["api_router"]

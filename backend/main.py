"""
ReadPilot Backend - FastAPI + Parlant Multi-Agent System

Main application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from api import chat_router, documents_router, users_router
from services.agent_service import agent_service

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="AI-powered reading companion with multi-agent architecture",
    debug=settings.DEBUG
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    print(f"🚀 Starting {settings.APP_NAME} v{settings.APP_VERSION}")

    # Initialize Parlant agents
    print("📦 Initializing Parlant agents...")
    success = await agent_service.initialize()

    if not success:
        print("❌ Failed to initialize agents. Some features may not work.")
    else:
        print("✅ All services initialized successfully")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("🛑 Shutting down services...")
    await agent_service.shutdown()
    print("✅ Shutdown complete")


# Include routers
app.include_router(chat_router, prefix=settings.API_V1_PREFIX)
app.include_router(documents_router, prefix=settings.API_V1_PREFIX)
app.include_router(users_router, prefix=settings.API_V1_PREFIX)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": "AI-powered reading companion",
        "status": "running",
        "agents": {
            "coordinator": "active",
            "summarizer": "active",
            "qa": "active",
            "note_builder": "active",
            "quiz_generator": "active"
        }
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2025-10-16T00:00:00Z"
    }


# API documentation
@app.get("/docs-info")
async def docs_info():
    """API documentation information"""
    return {
        "swagger_ui": "/docs",
        "redoc": "/redoc",
        "openapi_json": "/openapi.json"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info"
    )

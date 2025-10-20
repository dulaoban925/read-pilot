"""
Configuration management for ReadPilot backend
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # Application
    APP_NAME: str = "ReadPilot"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # API
    API_V1_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8000"]

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/readpilot"
    DB_ECHO: bool = False

    # Vector Database (Qdrant - Primary)
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_COLLECTION_NAME: str = "documents"
    USE_QDRANT: bool = True

    # Alternative: Pinecone (SaaS option - currently disabled)
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: str = "us-east-1"
    PINECONE_INDEX_NAME: str = "readpilot-documents"
    USE_PINECONE: bool = False

    # LLM Settings
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    DEFAULT_LLM_PROVIDER: str = "openai"  # "openai" or "anthropic"
    DEFAULT_MODEL: str = "gpt-4"
    EMBEDDING_MODEL: str = "text-embedding-3-small"

    # Parlant Settings
    PARLANT_SERVER_HOST: str = "localhost"
    PARLANT_SERVER_PORT: int = 8080

    # Context Settings
    MAX_CONVERSATION_HISTORY: int = 10
    MAX_CONTEXT_LENGTH: int = 8000

    # Document Processing
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: list[str] = [".pdf", ".txt", ".md", ".docx"]
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    # Redis (for caching)
    REDIS_URL: Optional[str] = "redis://localhost:6379"
    CACHE_TTL: int = 3600  # 1 hour

    # JWT Authentication
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

"""Application Configuration"""
from typing import List, Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # Project Info
    PROJECT_NAME: str = "ReadPilot API"
    DESCRIPTION: str = "AI-powered reading companion for intelligent document interaction"
    VERSION: str = "0.1.0"
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"

    # API Configuration
    API_V1_PREFIX: str = "/api/v1"

    # CORS
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:3001"],
        description="Allowed CORS origins"
    )

    # Database
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./readpilot.db",
        description="Database connection URL"
    )

    # Redis
    REDIS_URL: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL"
    )

    # Vector Database (ChromaDB)
    CHROMADB_PATH: str = Field(
        default="./data/chromadb",
        description="ChromaDB persistent storage path"
    )
    CHROMADB_COLLECTION_NAME: str = "document_chunks"

    # AI/LLM Configuration
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key")
    ANTHROPIC_API_KEY: str = Field(default="", description="Anthropic API key")
    QWEN_API_KEY: str = Field(default="", description="阿里云千问 API key")

    # AI Provider Settings
    PRIMARY_AI_PROVIDER: Literal["openai", "anthropic", "qwen"] = Field(
        default="qwen",
        description="Primary AI provider for LLM tasks"
    )
    FALLBACK_AI_PROVIDER: Literal["openai", "anthropic", "qwen"] = Field(
        default="openai",
        description="Fallback AI provider when primary fails"
    )

    LLM_PROVIDER: Literal["openai", "anthropic", "qwen"] = "qwen"
    LLM_MODEL: str = "qwen-flash"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    EMBEDDING_DIMENSION: int = 1536

    # File Upload
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".epub", ".txt", ".md", ".docx"]
    UPLOAD_DIR: str = "./data/documents"

    # Text Processing
    CHUNK_SIZE: int = 800  # tokens
    CHUNK_OVERLAP: int = 100  # tokens
    MAX_CONCURRENT_CHUNKS: int = 10

    # Security
    SECRET_KEY: str = Field(
        default="your-secret-key-change-this-in-production",
        description="Secret key for JWT encoding"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days


settings = Settings()

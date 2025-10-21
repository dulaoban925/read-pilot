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

    # Vector Database (Qdrant)
    QDRANT_URL: str = Field(
        default="http://localhost:6333",
        description="Qdrant server URL"
    )
    QDRANT_COLLECTION_NAME: str = "readpilot_documents"

    # AI/LLM Configuration
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API key")
    ANTHROPIC_API_KEY: str = Field(default="", description="Anthropic API key")
    LLM_PROVIDER: Literal["openai", "anthropic", "ollama"] = "openai"
    LLM_MODEL: str = "gpt-4o-mini"

    # File Upload
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".epub", ".txt", ".md", ".docx"]
    UPLOAD_DIR: str = "./data/documents"

    # Security
    SECRET_KEY: str = Field(
        default="your-secret-key-change-this-in-production",
        description="Secret key for JWT encoding"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days


settings = Settings()

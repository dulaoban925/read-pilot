"""AI Service Module"""
from typing import Literal

from app.core.ai.anthropic_service import AnthropicLLMService
from app.core.ai.base import BaseEmbeddingService, BaseLLMService
from app.core.ai.openai_service import OpenAIEmbeddingService, OpenAILLMService
from app.core.ai.qwen_service import QwenEmbeddingService, QwenLLMService
from app.core.config import settings


def get_embedding_service() -> BaseEmbeddingService:
    """
    Get the configured embedding service.

    Embedding 服务跟随 PRIMARY_AI_PROVIDER 配置,确保与 LLM 提供商一致。

    Returns:
        BaseEmbeddingService: The embedding service instance

    Raises:
        ValueError: If the configured provider doesn't have an API key or doesn't support embeddings
    """
    provider = settings.PRIMARY_AI_PROVIDER

    # 根据主要 AI 提供商选择 embedding 服务
    if provider == "qwen":
        if settings.QWEN_API_KEY:
            return QwenEmbeddingService(api_key=settings.QWEN_API_KEY)
        else:
            raise ValueError("QWEN_API_KEY is not configured but PRIMARY_AI_PROVIDER is set to 'qwen'")

    elif provider == "openai":
        if settings.OPENAI_API_KEY:
            return OpenAIEmbeddingService()
        else:
            raise ValueError("OPENAI_API_KEY is not configured but PRIMARY_AI_PROVIDER is set to 'openai'")

    elif provider == "anthropic":
        # Anthropic 不支持 embedding,降级到 OpenAI 或 Qwen
        if settings.OPENAI_API_KEY:
            return OpenAIEmbeddingService()
        elif settings.QWEN_API_KEY:
            return QwenEmbeddingService(api_key=settings.QWEN_API_KEY)
        else:
            raise ValueError(
                "Anthropic doesn't support embeddings. "
                "Please configure OPENAI_API_KEY or QWEN_API_KEY for embedding service."
            )

    else:
        raise ValueError(f"Unsupported PRIMARY_AI_PROVIDER: {provider}")


def get_llm_service(
    provider: Literal["openai", "anthropic"] | None = None
) -> BaseLLMService:
    """
    Get the configured LLM service.

    Args:
        provider: Optional provider override. If None, uses settings.LLM_PROVIDER

    Returns:
        BaseLLMService: The LLM service instance

    Raises:
        ValueError: If an unsupported provider is specified
    """
    provider = provider or settings.LLM_PROVIDER

    if provider == "openai":
        return OpenAILLMService()
    elif provider == "anthropic":
        return AnthropicLLMService()
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


__all__ = [
    "BaseEmbeddingService",
    "BaseLLMService",
    "OpenAIEmbeddingService",
    "OpenAILLMService",
    "AnthropicLLMService",
    "get_embedding_service",
    "get_llm_service",
]

"""
AI 服务 (AI Service)

提供统一的 AI 功能接口,支持多个 AI 提供商:
- 文档摘要生成
- 问答对话
- 提供商自动切换和回退
"""

from typing import Dict, List, Optional
from uuid import UUID

from app.core.ai.anthropic_service import AnthropicLLMService
from app.core.ai.base import BaseLLMService
from app.core.ai.openai_service import OpenAILLMService
from app.core.ai.qwen_service import QwenLLMService
from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class AIServiceError(Exception):
    """AI 服务错误"""

    pass


class AIService:
    """
    AI 服务类

    管理多个 AI 提供商,提供统一的接口和自动回退机制
    """

    def __init__(
        self,
        primary_provider: str = "qwen",
        fallback_provider: Optional[str] = "openai",
    ):
        """
        初始化 AI 服务

        Args:
            primary_provider: 主要提供商 (openai/anthropic/qwen)
            fallback_provider: 回退提供商
        """
        self.primary_provider_name = primary_provider
        self.fallback_provider_name = fallback_provider

        # 初始化提供商
        self.providers: Dict[str, BaseLLMService] = {}
        self._init_providers()

        logger.info(
            "ai_service_initialized",
            primary=primary_provider,
            fallback=fallback_provider,
        )

    def _init_providers(self) -> None:
        """初始化所有可用的 AI 提供商"""
        # 初始化 OpenAI
        if settings.OPENAI_API_KEY:
            try:
                self.providers["openai"] = OpenAILLMService(
                    api_key=settings.OPENAI_API_KEY
                )
                logger.info("openai_provider_initialized")
            except Exception as e:
                logger.warning("openai_provider_init_failed", error=str(e))

        # 初始化 Anthropic
        if settings.ANTHROPIC_API_KEY:
            try:
                self.providers["anthropic"] = AnthropicLLMService(
                    api_key=settings.ANTHROPIC_API_KEY
                )
                logger.info("anthropic_provider_initialized")
            except Exception as e:
                logger.warning("anthropic_provider_init_failed", error=str(e))

        # 初始化千问
        if settings.QWEN_API_KEY:
            try:
                self.providers["qwen"] = QwenLLMService(
                    api_key=settings.QWEN_API_KEY,
                    model=settings.LLM_MODEL if settings.LLM_PROVIDER == "qwen" else "qwen-flash",
                )
                logger.info("qwen_provider_initialized")
            except Exception as e:
                logger.warning("qwen_provider_init_failed", error=str(e))

        if not self.providers:
            raise AIServiceError("No AI providers available")

    def _get_provider(self, prefer_provider: Optional[str] = None) -> BaseLLMService:
        """
        获取 AI 提供商实例

        Args:
            prefer_provider: 首选提供商名称

        Returns:
            BaseLLMService 实例

        Raises:
            AIServiceError: 无可用提供商
        """
        # 如果指定了首选提供商,尝试使用它
        if prefer_provider and prefer_provider in self.providers:
            return self.providers[prefer_provider]

        # 使用主要提供商
        if self.primary_provider_name in self.providers:
            return self.providers[self.primary_provider_name]

        # 使用回退提供商
        if (
            self.fallback_provider_name
            and self.fallback_provider_name in self.providers
        ):
            logger.warning(
                "using_fallback_provider", provider=self.fallback_provider_name
            )
            return self.providers[self.fallback_provider_name]

        # 使用任何可用的提供商
        if self.providers:
            provider_name = next(iter(self.providers))
            logger.warning("using_any_available_provider", provider=provider_name)
            return self.providers[provider_name]

        raise AIServiceError("No AI providers available")

    async def generate_summary(
        self,
        text: str,
        depth: str = "detailed",
        prefer_provider: Optional[str] = None,
    ) -> Dict:
        """
        生成文档摘要

        Args:
            text: 文档文本
            depth: 摘要深度 (brief/detailed)
            prefer_provider: 首选 AI 提供商

        Returns:
            摘要字典,包含 abstract, key_insights, main_concepts 等字段

        Raises:
            AIServiceError: 摘要生成失败
        """
        try:
            provider = self._get_provider(prefer_provider)
            logger.info(
                "generating_summary",
                provider=provider.__class__.__name__,
                text_length=len(text),
                depth=depth,
            )

            # 调用提供商生成摘要
            summary = await provider.generate_summary(text, depth=depth)

            logger.info(
                "summary_generated",
                provider=provider.__class__.__name__,
                has_abstract=bool(summary.get("abstract")),
                insights_count=len(summary.get("key_insights", [])),
                concepts_count=len(summary.get("main_concepts", [])),
            )

            return summary

        except Exception as e:
            logger.error(
                "summary_generation_failed",
                provider=prefer_provider or self.primary_provider_name,
                error=str(e),
            )

            # 尝试使用回退提供商
            if (
                prefer_provider != self.fallback_provider_name
                and self.fallback_provider_name in self.providers
            ):
                logger.info("retrying_with_fallback_provider")
                try:
                    return await self.generate_summary(
                        text, depth, prefer_provider=self.fallback_provider_name
                    )
                except Exception as fallback_error:
                    logger.error(
                        "fallback_provider_failed", error=str(fallback_error)
                    )

            raise AIServiceError(f"Failed to generate summary: {str(e)}")

    async def generate_answer(
        self,
        question: str,
        context_chunks: List[str],
        chat_history: Optional[List[Dict]] = None,
        prefer_provider: Optional[str] = None,
    ) -> Dict:
        """
        生成问答回答

        Args:
            question: 用户问题
            context_chunks: 相关文档片段列表
            chat_history: 对话历史
            prefer_provider: 首选 AI 提供商

        Returns:
            回答字典,包含 answer, sources, confidence 等字段

        Raises:
            AIServiceError: 回答生成失败
        """
        try:
            provider = self._get_provider(prefer_provider)
            logger.info(
                "generating_answer",
                provider=provider.__class__.__name__,
                question_length=len(question),
                context_chunks_count=len(context_chunks),
                has_history=bool(chat_history),
            )

            # 调用提供商生成回答
            answer = await provider.generate_answer(
                question=question,
                context_chunks=context_chunks,
                chat_history=chat_history or [],
            )

            logger.info(
                "answer_generated",
                provider=provider.__class__.__name__,
                has_answer=bool(answer.get("answer")),
                sources_count=len(answer.get("sources", [])),
            )

            return answer

        except Exception as e:
            logger.error(
                "answer_generation_failed",
                provider=prefer_provider or self.primary_provider_name,
                error=str(e),
            )

            # 尝试使用回退提供商
            if (
                prefer_provider != self.fallback_provider_name
                and self.fallback_provider_name in self.providers
            ):
                logger.info("retrying_with_fallback_provider")
                try:
                    return await self.generate_answer(
                        question,
                        context_chunks,
                        chat_history,
                        prefer_provider=self.fallback_provider_name,
                    )
                except Exception as fallback_error:
                    logger.error(
                        "fallback_provider_failed", error=str(fallback_error)
                    )

            raise AIServiceError(f"Failed to generate answer: {str(e)}")


# 全局实例
_ai_service: Optional[AIService] = None


def get_ai_service() -> AIService:
    """
    获取全局 AI 服务实例

    Returns:
        AIService 实例
    """
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService(
            primary_provider=getattr(settings, "PRIMARY_AI_PROVIDER", "qwen"),
            fallback_provider=getattr(settings, "FALLBACK_AI_PROVIDER", "openai"),
        )
    return _ai_service

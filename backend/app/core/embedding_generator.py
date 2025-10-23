"""
向量生成器 (Embedding Generator)

使用 OpenAI 的 text-embedding-3-small 模型生成文本向量
"""

from typing import List

from openai import AsyncOpenAI

from app.core.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class EmbeddingGeneratorError(Exception):
    """向量生成错误"""

    pass


class EmbeddingGenerator:
    """
    向量生成器类

    负责将文本转换为向量表示,用于向量数据库存储和语义搜索
    """

    def __init__(
        self,
        model: str = "text-embedding-3-small",
        api_key: str | None = None,
    ):
        """
        初始化向量生成器

        Args:
            model: OpenAI 向量模型名称
            api_key: OpenAI API 密钥
        """
        self.model = model
        self.client = AsyncOpenAI(api_key=api_key or settings.OPENAI_API_KEY)
        logger.info("embedding_generator_initialized", model=model)

    async def generate_embedding(self, text: str) -> List[float]:
        """
        生成单个文本的向量

        Args:
            text: 输入文本

        Returns:
            向量 (浮点数列表)

        Raises:
            EmbeddingGeneratorError: 生成失败
        """
        if not text or not text.strip():
            raise EmbeddingGeneratorError("Input text is empty")

        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=text,
                encoding_format="float",
            )

            embedding = response.data[0].embedding

            logger.debug(
                "embedding_generated",
                text_length=len(text),
                embedding_dim=len(embedding),
            )

            return embedding

        except Exception as e:
            logger.error(
                "embedding_generation_failed",
                model=self.model,
                text_length=len(text),
                error=str(e),
            )
            raise EmbeddingGeneratorError(f"Failed to generate embedding: {e}")

    async def generate_embeddings_batch(
        self, texts: List[str], batch_size: int = 100
    ) -> List[List[float]]:
        """
        批量生成文本向量

        Args:
            texts: 文本列表
            batch_size: 批处理大小,默认 100

        Returns:
            向量列表

        Raises:
            EmbeddingGeneratorError: 生成失败
        """
        if not texts:
            return []

        # 过滤空文本
        valid_texts = [text for text in texts if text and text.strip()]
        if not valid_texts:
            raise EmbeddingGeneratorError("All input texts are empty")

        try:
            embeddings = []

            # 分批处理
            for i in range(0, len(valid_texts), batch_size):
                batch = valid_texts[i : i + batch_size]

                response = await self.client.embeddings.create(
                    model=self.model,
                    input=batch,
                    encoding_format="float",
                )

                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)

                logger.debug(
                    "batch_embeddings_generated",
                    batch_num=i // batch_size + 1,
                    batch_size=len(batch),
                    total_processed=len(embeddings),
                )

            logger.info(
                "embeddings_batch_generated",
                total_texts=len(valid_texts),
                embedding_dim=len(embeddings[0]) if embeddings else 0,
            )

            return embeddings

        except Exception as e:
            logger.error(
                "batch_embedding_generation_failed",
                model=self.model,
                num_texts=len(valid_texts),
                error=str(e),
            )
            raise EmbeddingGeneratorError(f"Failed to generate batch embeddings: {e}")

    async def get_embedding_dimension(self) -> int:
        """
        获取向量维度

        Returns:
            向量维度

        Raises:
            EmbeddingGeneratorError: 获取失败
        """
        try:
            # 使用简单文本测试
            test_embedding = await self.generate_embedding("test")
            return len(test_embedding)
        except Exception as e:
            logger.error("failed_to_get_embedding_dimension", error=str(e))
            raise EmbeddingGeneratorError(f"Failed to get embedding dimension: {e}")


# 全局实例 (延迟初始化)
_embedding_generator: EmbeddingGenerator | None = None


def get_embedding_generator() -> EmbeddingGenerator:
    """
    获取全局向量生成器实例

    Returns:
        EmbeddingGenerator 实例
    """
    global _embedding_generator
    if _embedding_generator is None:
        _embedding_generator = EmbeddingGenerator()
    return _embedding_generator

"""
阿里云千问 (Qwen) LLM Service 实现
"""

import json
from typing import Any, Dict, List, Optional

import dashscope
from dashscope import Generation, TextEmbedding
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.ai.base import BaseLLMService, BaseEmbeddingService
from app.utils.logger import get_logger

logger = get_logger(__name__)


class QwenLLMService(BaseLLMService):
    """阿里云千问 LLM 服务实现"""

    def __init__(
        self,
        api_key: str,
        model: str = "qwen-flash",
        base_url: Optional[str] = None,
    ):
        """
        初始化千问 LLM 服务

        Args:
            api_key: 阿里云 API Key
            model: 模型名称 (qwen-flash, qwen-plus, qwen-turbo 等)
            base_url: API 基础 URL (可选,默认使用官方 API)
        """
        self.api_key = api_key
        self.model = model
        dashscope.api_key = api_key
        logger.info("qwen_provider_initialized", model=model)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        生成对话补全

        Args:
            messages: 对话消息列表
            temperature: 温度参数
            max_tokens: 最大生成 token 数
            **kwargs: 其他参数

        Returns:
            包含生成结果的字典
        """
        try:
            response = Generation.call(
                model=self.model,
                messages=messages,
                result_format="message",
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs,
            )

            if response.status_code == 200:
                output = response.output
                content = output.choices[0].message.content

                # 处理 usage 字段 (可能不存在)
                usage = {}
                if hasattr(response, 'usage') and response.usage:
                    usage = {
                        "prompt_tokens": getattr(response.usage, 'input_tokens', 0),
                        "completion_tokens": getattr(response.usage, 'output_tokens', 0),
                        "total_tokens": getattr(response.usage, 'total_tokens', 0),
                    }

                return {
                    "content": content,
                    "model": self.model,
                    "usage": usage,
                }
            else:
                raise Exception(
                    f"Qwen API error: {response.code} - {response.message}"
                )

        except Exception as e:
            logger.error("qwen_completion_failed", error=str(e))
            raise

    async def generate_streaming_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 2000,
        **kwargs,
    ):
        """
        生成流式对话补全

        Args:
            messages: 对话消息列表
            temperature: 温度参数
            max_tokens: 最大生成 token 数
            **kwargs: 其他参数

        Yields:
            生成的文本片段
        """
        try:
            responses = Generation.call(
                model=self.model,
                messages=messages,
                result_format="message",
                stream=True,
                temperature=temperature,
                max_tokens=max_tokens,
                incremental_output=True,
                **kwargs,
            )

            for response in responses:
                if response.status_code == 200:
                    content = response.output.choices[0].message.content
                    yield content
                else:
                    raise Exception(
                        f"Qwen API error: {response.code} - {response.message}"
                    )

        except Exception as e:
            logger.error("qwen_streaming_completion_failed", error=str(e))
            raise

    async def generate_summary(
        self, text: str, depth: str = "detailed", **kwargs
    ) -> Dict[str, Any]:
        """
        生成文档摘要

        Args:
            text: 输入文本
            depth: 摘要深度 (brief 或 detailed)
            **kwargs: 其他参数

        Returns:
            包含摘要信息的字典
        """
        # 根据深度选择不同的提示词
        if depth == "brief":
            prompt = f"""请为以下文档生成一个简要摘要。

要求:
1. 用1-2段话概括文档核心内容
2. 提取3-5个关键见解
3. 列出3-5个主要概念

文档内容:
{text[:4000]}

请以JSON格式返回,包含以下字段:
{{"abstract": "简要摘要文字", "key_insights": ["见解1", "见解2", "..."], "main_concepts": ["概念1", "概念2", "..."]}}"""
        else:  # detailed
            prompt = f"""请为以下文档生成一个详细摘要。

要求:
1. 用3-5段话全面概括文档内容,包括背景、核心观点、支持论据和结论
2. 提取5-8个关键见解,深入分析文档的重要发现和创新点
3. 列出5-8个主要概念,包括核心术语和重要理论

文档内容:
{text[:8000]}

请以JSON格式返回,包含以下字段:
{{"abstract": "详细摘要文字", "key_insights": ["见解1", "见解2", "..."], "main_concepts": ["概念1", "概念2", "..."]}}"""

        messages = [
            {
                "role": "system",
                "content": "你是一个专业的文档分析助手,擅长提取文档的核心内容和关键信息。请严格按照JSON格式返回结果。",
            },
            {"role": "user", "content": prompt},
        ]

        try:
            response = await self.generate_completion(
                messages=messages, temperature=0.3, max_tokens=2000
            )

            # 解析响应内容
            content = response["content"]

            # 尝试提取 JSON (处理可能的 markdown 代码块)
            try:
                # 如果响应包含 markdown 代码块,提取其中的 JSON
                if "```json" in content:
                    json_str = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    json_str = content.split("```")[1].split("```")[0].strip()
                else:
                    json_str = content.strip()

                summary_data = json.loads(json_str)

                return {
                    "abstract": summary_data.get("abstract", ""),
                    "key_insights": summary_data.get("key_insights", []),
                    "main_concepts": summary_data.get("main_concepts", []),
                    "model": response["model"],
                    "depth": depth,
                }

            except (json.JSONDecodeError, KeyError, IndexError) as e:
                logger.warning(
                    "json_parse_failed", error=str(e), content=content[:200]
                )
                # 如果 JSON 解析失败,返回原始内容
                return {
                    "abstract": content,
                    "key_insights": [],
                    "main_concepts": [],
                    "model": response["model"],
                    "depth": depth,
                    "parse_error": str(e),
                }

        except Exception as e:
            logger.error("summary_generation_failed", error=str(e))
            raise

    async def generate_answer(
        self,
        question: str,
        context_chunks: List[str],
        chat_history: Optional[List[Dict]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        基于上下文生成问题答案

        Args:
            question: 用户问题
            context_chunks: 相关文档片段列表
            chat_history: 聊天历史 (可选)
            **kwargs: 其他参数

        Returns:
            包含答案的字典
        """
        # 构建上下文
        context = "\n\n---\n\n".join(context_chunks[:5])  # 限制上下文长度

        # 构建消息
        messages = []

        # 系统消息
        system_message = """你是一个专业的文档问答助手。请基于提供的文档内容回答用户的问题。

要求:
1. 答案必须基于提供的文档内容
2. 如果文档中没有相关信息,请明确说明
3. 保持回答简洁、准确、有条理
4. 如果适用,可以引用文档中的关键句子"""

        messages.append({"role": "system", "content": system_message})

        # 添加聊天历史
        if chat_history:
            messages.extend(chat_history[-5:])  # 只保留最近 5 轮对话

        # 构建用户问题
        user_message = f"""文档内容:
{context}

问题: {question}

请基于以上文档内容回答问题。"""

        messages.append({"role": "user", "content": user_message})

        try:
            response = await self.generate_completion(
                messages=messages, temperature=0.5, max_tokens=1500
            )

            return {
                "answer": response["content"],
                "model": response["model"],
                "sources": len(context_chunks),
            }

        except Exception as e:
            logger.error("answer_generation_failed", error=str(e))
            raise


class QwenEmbeddingService(BaseEmbeddingService):
    """阿里云千问 Embedding 服务实现"""

    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-v3",
    ):
        """
        初始化千问 Embedding 服务

        Args:
            api_key: 阿里云 API Key
            model: 模型名称 (text-embedding-v1, text-embedding-v2, text-embedding-v3)
        """
        self.api_key = api_key
        self.model = model
        dashscope.api_key = api_key
        logger.info("qwen_embedding_service_initialized", model=model)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def generate_embeddings(
        self, texts: List[str], **kwargs
    ) -> List[List[float]]:
        """
        生成文本的向量表示

        Args:
            texts: 文本列表
            **kwargs: 其他参数

        Returns:
            向量列表
        """
        try:
            # 阿里云 DashScope 的 TextEmbedding API
            response = TextEmbedding.call(
                model=self.model,
                input=texts,
            )

            if response.status_code == 200:
                embeddings = []
                for item in response.output['embeddings']:
                    embeddings.append(item['embedding'])

                logger.info(
                    "embeddings_generated",
                    model=self.model,
                    count=len(embeddings),
                )
                return embeddings
            else:
                raise Exception(
                    f"Qwen Embedding API error: {response.code} - {response.message}"
                )

        except Exception as e:
            logger.error("embedding_generation_failed", error=str(e))
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )
    async def generate_embedding(self, text: str, **kwargs) -> List[float]:
        """
        生成单个文本的向量表示

        Args:
            text: 文本
            **kwargs: 其他参数

        Returns:
            向量
        """
        embeddings = await self.generate_embeddings([text], **kwargs)
        return embeddings[0]

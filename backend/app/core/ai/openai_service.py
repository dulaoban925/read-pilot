"""OpenAI Service Implementation"""
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.ai.base import BaseEmbeddingService, BaseLLMService
from app.core.config import settings


class OpenAIEmbeddingService(BaseEmbeddingService):
    """OpenAI embedding service implementation"""

    def __init__(self, api_key: Optional[str] = None):
        self.client = AsyncOpenAI(api_key=api_key or settings.OPENAI_API_KEY)
        self.default_model = settings.EMBEDDING_MODEL

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def generate_embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None
    ) -> List[List[float]]:
        """Generate embeddings for multiple texts with retry logic"""
        if not texts:
            return []

        response = await self.client.embeddings.create(
            model=model or self.default_model,
            input=texts
        )
        return [item.embedding for item in response.data]

    async def generate_embedding(
        self,
        text: str,
        model: Optional[str] = None
    ) -> List[float]:
        """Generate embedding for a single text"""
        embeddings = await self.generate_embeddings([text], model)
        return embeddings[0] if embeddings else []


class OpenAILLMService(BaseLLMService):
    """OpenAI LLM service implementation"""

    def __init__(self, api_key: Optional[str] = None):
        self.client = AsyncOpenAI(api_key=api_key or settings.OPENAI_API_KEY)
        self.default_model = settings.LLM_MODEL

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Generate completion with retry logic"""
        response = await self.client.chat.completions.create(
            model=model or self.default_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs
        )

        return {
            "content": response.choices[0].message.content,
            "model": response.model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            "finish_reason": response.choices[0].finish_reason,
        }

    async def generate_streaming_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ):
        """Generate streaming completion"""
        stream = await self.client.chat.completions.create(
            model=model or self.default_model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def generate_summary(
        self,
        text: str,
        depth: str = "detailed",
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Generate document summary"""
        import json

        # 根据深度构建提示词
        if depth == "brief":
            prompt = f"""请为以下文档生成一个简要摘要。

要求:
1. 用1-2段话概括文档核心内容
2. 提取3-5个关键见解
3. 列出3-5个主要概念

文档内容:
{text[:4000]}  # 限制长度避免token超限

请以JSON格式返回,包含以下字段:
{{
  "abstract": "简要摘要文字",
  "key_insights": ["见解1", "见解2", "见解3"],
  "main_concepts": ["概念1", "概念2", "概念3"]
}}"""
        else:  # detailed
            prompt = f"""请为以下文档生成一个详细摘要。

要求:
1. 用3-5段话全面概括文档内容
2. 提取5-8个关键见解
3. 列出5-8个主要概念

文档内容:
{text[:8000]}  # 详细模式允许更多内容

请以JSON格式返回,包含以下字段:
{{
  "abstract": "详细摘要文字",
  "key_insights": ["见解1", "见解2", ...],
  "main_concepts": ["概念1", "概念2", ...]
}}"""

        messages = [
            {"role": "system", "content": "你是一个专业的文档分析助手,擅长提取文档的核心内容和关键信息。"},
            {"role": "user", "content": prompt}
        ]

        response = await self.generate_completion(
            messages=messages,
            temperature=0.3,  # 降低温度以获得更稳定的输出
            max_tokens=2000,
            **kwargs
        )

        # 解析JSON响应
        try:
            content = response["content"]
            # 尝试提取JSON (可能包含在```json...```中)
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            summary_data = json.loads(content)

            # 确保返回的字段存在
            return {
                "abstract": summary_data.get("abstract", ""),
                "key_insights": summary_data.get("key_insights", []),
                "main_concepts": summary_data.get("main_concepts", []),
                "model": response["model"],
                "depth": depth,
            }
        except (json.JSONDecodeError, KeyError, IndexError) as e:
            # 如果解析失败,返回原始内容
            return {
                "abstract": response["content"],
                "key_insights": [],
                "main_concepts": [],
                "model": response["model"],
                "depth": depth,
                "parse_error": str(e),
            }

    async def generate_answer(
        self,
        question: str,
        context_chunks: List[str],
        chat_history: Optional[List[Dict]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Generate answer based on context"""
        # 构建上下文
        context_text = "\n\n---\n\n".join(context_chunks[:5])  # 限制最多5个chunk

        # 构建提示词
        prompt = f"""基于以下文档内容回答用户问题。

文档内容:
{context_text}

请根据文档内容准确回答问题,并引用相关段落。如果文档中没有相关信息,请明确说明。"""

        messages = [
            {"role": "system", "content": prompt}
        ]

        # 添加对话历史
        if chat_history:
            messages.extend(chat_history[-5:])  # 最多保留最近5轮对话

        # 添加当前问题
        messages.append({"role": "user", "content": question})

        response = await self.generate_completion(
            messages=messages,
            temperature=0.7,
            max_tokens=1000,
            **kwargs
        )

        return {
            "answer": response["content"],
            "sources": context_chunks[:3],  # 返回前3个相关段落作为来源
            "model": response["model"],
            "confidence": "medium",  # 可以基于response添加置信度逻辑
        }

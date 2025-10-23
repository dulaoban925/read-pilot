"""Anthropic Service Implementation"""
from typing import Any, Dict, List, Optional

from anthropic import AsyncAnthropic
from tenacity import retry, stop_after_attempt, wait_exponential

from app.core.ai.base import BaseLLMService
from app.core.config import settings


class AnthropicLLMService(BaseLLMService):
    """Anthropic Claude LLM service implementation"""

    def __init__(self, api_key: Optional[str] = None):
        self.client = AsyncAnthropic(api_key=api_key or settings.ANTHROPIC_API_KEY)
        self.default_model = "claude-3-5-sonnet-20241022"  # Latest Claude model

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
        # Convert messages format from OpenAI to Anthropic
        system_messages = [m["content"] for m in messages if m["role"] == "system"]
        user_messages = [m for m in messages if m["role"] != "system"]

        response = await self.client.messages.create(
            model=model or self.default_model,
            messages=user_messages,
            system=system_messages[0] if system_messages else None,
            temperature=temperature,
            max_tokens=max_tokens or 4096,
            **kwargs
        )

        return {
            "content": response.content[0].text,
            "model": response.model,
            "usage": {
                "prompt_tokens": response.usage.input_tokens,
                "completion_tokens": response.usage.output_tokens,
                "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
            },
            "finish_reason": response.stop_reason,
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
        # Convert messages format from OpenAI to Anthropic
        system_messages = [m["content"] for m in messages if m["role"] == "system"]
        user_messages = [m for m in messages if m["role"] != "system"]

        async with self.client.messages.stream(
            model=model or self.default_model,
            messages=user_messages,
            system=system_messages[0] if system_messages else None,
            temperature=temperature,
            max_tokens=max_tokens or 4096,
            **kwargs
        ) as stream:
            async for text in stream.text_stream:
                yield text

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
{text[:4000]}

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
{text[:8000]}

请以JSON格式返回,包含以下字段:
{{
  "abstract": "详细摘要文字",
  "key_insights": ["见解1", "见解2", ...],
  "main_concepts": ["概念1", "概念2", ...]
}}"""

        messages = [
            {"role": "user", "content": prompt}
        ]

        response = await self.generate_completion(
            messages=messages,
            temperature=0.3,
            max_tokens=2000,
            **kwargs
        )

        # 解析JSON响应
        try:
            content = response["content"]
            # 尝试提取JSON
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()

            summary_data = json.loads(content)

            return {
                "abstract": summary_data.get("abstract", ""),
                "key_insights": summary_data.get("key_insights", []),
                "main_concepts": summary_data.get("main_concepts", []),
                "model": response["model"],
                "depth": depth,
            }
        except (json.JSONDecodeError, KeyError, IndexError) as e:
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
        context_text = "\n\n---\n\n".join(context_chunks[:5])

        prompt = f"""基于以下文档内容回答用户问题。

文档内容:
{context_text}

请根据文档内容准确回答问题,并引用相关段落。如果文档中没有相关信息,请明确说明。"""

        messages = []

        if chat_history:
            messages.extend(chat_history[-5:])

        messages.append({"role": "user", "content": f"{prompt}\n\n问题: {question}"})

        response = await self.generate_completion(
            messages=messages,
            temperature=0.7,
            max_tokens=1000,
            **kwargs
        )

        return {
            "answer": response["content"],
            "sources": context_chunks[:3],
            "model": response["model"],
            "confidence": "medium",
        }

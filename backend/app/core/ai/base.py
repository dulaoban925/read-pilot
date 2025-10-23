"""Base AI Service Abstractions"""
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseEmbeddingService(ABC):
    """Abstract base class for embedding services"""

    @abstractmethod
    async def generate_embeddings(
        self,
        texts: List[str],
        model: Optional[str] = None
    ) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to embed
            model: Optional model name override

        Returns:
            List of embedding vectors
        """
        pass

    @abstractmethod
    async def generate_embedding(
        self,
        text: str,
        model: Optional[str] = None
    ) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Text string to embed
            model: Optional model name override

        Returns:
            Embedding vector
        """
        pass


class BaseLLMService(ABC):
    """Abstract base class for LLM services"""

    @abstractmethod
    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Generate a completion for the given messages.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            model: Optional model name override
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters

        Returns:
            Dict containing 'content', 'model', 'usage', etc.
        """
        pass

    @abstractmethod
    async def generate_streaming_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any
    ):
        """
        Generate a streaming completion for the given messages.

        Args:
            messages: List of message dicts with 'role' and 'content' keys
            model: Optional model name override
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters

        Yields:
            Chunks of generated text
        """
        pass

    @abstractmethod
    async def generate_summary(
        self,
        text: str,
        depth: str = "detailed",
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Generate a summary for the given text.

        Args:
            text: Text to summarize
            depth: Summary depth ('brief' or 'detailed')
            **kwargs: Additional provider-specific parameters

        Returns:
            Dict containing 'abstract', 'key_insights', 'main_concepts', etc.
        """
        pass

    @abstractmethod
    async def generate_answer(
        self,
        question: str,
        context_chunks: List[str],
        chat_history: Optional[List[Dict]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Generate an answer to a question based on context.

        Args:
            question: User's question
            context_chunks: Relevant document chunks
            chat_history: Previous conversation messages
            **kwargs: Additional provider-specific parameters

        Returns:
            Dict containing 'answer', 'sources', 'confidence', etc.
        """
        pass

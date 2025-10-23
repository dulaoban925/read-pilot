"""Redis Cache Manager"""
import json
from typing import Any, Optional

import redis.asyncio as redis

from app.core.config import settings


class CacheManager:
    """Redis cache manager for caching AI responses and frequently accessed data"""

    def __init__(self, redis_url: str = settings.REDIS_URL):
        self.redis_url = redis_url
        self._redis: Optional[redis.Redis] = None

    async def connect(self) -> None:
        """Establish Redis connection"""
        self._redis = await redis.from_url(
            self.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )

    async def close(self) -> None:
        """Close Redis connection"""
        if self._redis:
            await self._redis.close()

    @property
    def redis(self) -> redis.Redis:
        """Get Redis client instance"""
        if self._redis is None:
            raise RuntimeError("Redis connection not established. Call connect() first.")
        return self._redis

    async def get(self, key: str) -> Optional[str]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value as string, or None if not found
        """
        return await self.redis.get(key)

    async def set(
        self,
        key: str,
        value: str,
        expire: int = 3600
    ) -> bool:
        """
        Set value in cache with expiration.

        Args:
            key: Cache key
            value: Value to cache (string)
            expire: Expiration time in seconds (default: 1 hour)

        Returns:
            True if successful
        """
        return await self.redis.setex(key, expire, value)

    async def delete(self, key: str) -> int:
        """
        Delete key from cache.

        Args:
            key: Cache key

        Returns:
            Number of keys deleted
        """
        return await self.redis.delete(key)

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if key exists
        """
        return await self.redis.exists(key) > 0

    async def get_json(self, key: str) -> Optional[Any]:
        """
        Get JSON value from cache.

        Args:
            key: Cache key

        Returns:
            Deserialized JSON value, or None if not found
        """
        value = await self.get(key)
        if value is None:
            return None
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return None

    async def set_json(
        self,
        key: str,
        value: Any,
        expire: int = 3600
    ) -> bool:
        """
        Set JSON value in cache.

        Args:
            key: Cache key
            value: Value to cache (will be serialized to JSON)
            expire: Expiration time in seconds (default: 1 hour)

        Returns:
            True if successful
        """
        json_str = json.dumps(value, ensure_ascii=False)
        return await self.set(key, json_str, expire)

    async def increment(self, key: str, amount: int = 1) -> int:
        """
        Increment counter.

        Args:
            key: Cache key
            amount: Amount to increment by (default: 1)

        Returns:
            New value after increment
        """
        return await self.redis.incr(key, amount)

    async def get_many(self, keys: list[str]) -> dict[str, Optional[str]]:
        """
        Get multiple values from cache.

        Args:
            keys: List of cache keys

        Returns:
            Dictionary mapping keys to values
        """
        if not keys:
            return {}

        values = await self.redis.mget(keys)
        return dict(zip(keys, values))

    async def set_many(
        self,
        mapping: dict[str, str],
        expire: int = 3600
    ) -> None:
        """
        Set multiple values in cache.

        Args:
            mapping: Dictionary of key-value pairs
            expire: Expiration time in seconds (default: 1 hour)
        """
        if not mapping:
            return

        async with self.redis.pipeline() as pipe:
            for key, value in mapping.items():
                pipe.setex(key, expire, value)
            await pipe.execute()

    async def clear_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern.

        Args:
            pattern: Pattern to match (e.g., "summary:*")

        Returns:
            Number of keys deleted
        """
        cursor = 0
        deleted = 0

        while True:
            cursor, keys = await self.redis.scan(cursor, match=pattern, count=100)
            if keys:
                deleted += await self.redis.delete(*keys)
            if cursor == 0:
                break

        return deleted


# Global cache instance
cache_manager = CacheManager()


async def get_cache() -> CacheManager:
    """
    Dependency for getting cache manager.

    Usage:
        @app.get("/data")
        async def get_data(cache: CacheManager = Depends(get_cache)):
            ...
    """
    return cache_manager


def get_cache_service() -> CacheManager:
    """
    获取缓存服务实例 (同步版本)

    Returns:
        CacheManager 实例
    """
    return cache_manager

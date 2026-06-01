from __future__ import annotations

import json
import pickle
from datetime import timedelta
from typing import Any, Dict, List, Optional

from redis import asyncio as aioredis


class CacheService:

    DEFAULT_TTL = 3600
    SKILL_TTL = 7200
    SEARCH_TTL = 300
    WARM_CACHE_TTL = 3600

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379/0",
        key_prefix: str = "skill_library",
        default_ttl: int = DEFAULT_TTL,
    ):
        self.redis_url = redis_url
        self.key_prefix = key_prefix
        self.default_ttl = default_ttl
        self._redis: Optional[aioredis.Redis] = None
        self._connected = False

    async def _get_redis(self) -> aioredis.Redis:
        if self._redis is None or not self._connected:
            self._redis = aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=False,
            )
            self._connected = True
        return self._redis

    async def connect(self) -> None:
        await self._get_redis()
        self._connected = True

    async def disconnect(self) -> None:
        if self._redis:
            await self._redis.close()
            self._redis = None
            self._connected = False

    def _make_key(self, *parts: str) -> str:
        return f"{self.key_prefix}:{':'.join(parts)}"

    async def get(self, key: str) -> Optional[Any]:
        redis = await self._get_redis()
        try:
            raw = await redis.get(key)
            if raw is None:
                return None
            return pickle.loads(raw)
        except (pickle.PickleError, Exception):
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        redis = await self._get_redis()
        try:
            serialized = pickle.dumps(value)
            ttl = ttl if ttl is not None else self.default_ttl
            await redis.set(key, serialized, ex=ttl)
            return True
        except (pickle.PickleError, Exception):
            return False

    async def delete(self, key: str) -> bool:
        redis = await self._get_redis()
        try:
            result = await redis.delete(key)
            return result > 0
        except Exception:
            return False

    async def exists(self, key: str) -> bool:
        redis = await self._get_redis()
        try:
            result = await redis.exists(key)
            return result > 0
        except Exception:
            return False

    async def expire(self, key: str, ttl: int) -> bool:
        redis = await self._get_redis()
        try:
            return await redis.expire(key, ttl)
        except Exception:
            return False

    async def cache_skill(self, skill_id: str, skill_data: Dict[str, Any]) -> bool:
        key = self._make_key("skill", skill_id)
        return await self.set(key, skill_data, ttl=self.SKILL_TTL)

    async def get_cached_skill(self, skill_id: str) -> Optional[Dict[str, Any]]:
        key = self._make_key("skill", skill_id)
        return await self.get(key)

    async def invalidate_skill_cache(self, skill_id: str) -> bool:
        key = self._make_key("skill", skill_id)
        return await self.delete(key)

    async def cache_search_results(
        self,
        query: str,
        results: List[Dict[str, Any]],
        ttl: int = SEARCH_TTL,
        filters: Optional[Dict[str, Any]] = None,
    ) -> bool:
        query_key = self._normalize_query(query, filters)
        cache_key = self._make_key("search", query_key)
        cache_data = {
            "results": results,
            "query": query,
            "filters": filters,
        }
        return await self.set(cache_key, cache_data, ttl=ttl)

    async def get_cached_search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Optional[List[Dict[str, Any]]]:
        query_key = self._normalize_query(query, filters)
        cache_key = self._make_key("search", query_key)
        cached = await self.get(cache_key)
        if cached and isinstance(cached, dict):
            return cached.get("results")
        return None

    async def warm_cache(self, popular_skills: Optional[List[Dict[str, Any]]] = None) -> int:
        count = 0

        if popular_skills:
            for skill in popular_skills:
                skill_id = skill.get("id", "")
                if skill_id:
                    success = await self.cache_skill(str(skill_id), skill)
                    if success:
                        count += 1

        await self._cache_dashboard_stats()
        await self._cache_category_index()

        return count

    async def _cache_dashboard_stats(self) -> None:
        pass

    async def _cache_category_index(self) -> None:
        pass

    async def cache_categories(self, categories: List[Dict[str, Any]]) -> bool:
        key = self._make_key("categories")
        return await self.set(key, categories, ttl=self.WARM_CACHE_TTL)

    async def get_cached_categories(self) -> Optional[List[Dict[str, Any]]]:
        key = self._make_key("categories")
        return await self.get(key)

    async def cache_popular_skills(
        self,
        skills: List[Dict[str, Any]],
        days: int = 30,
    ) -> bool:
        key = self._make_key("popular_skills", str(days))
        return await self.set(key, skills, ttl=self.SEARCH_TTL)

    async def get_cached_popular_skills(
        self, days: int = 30
    ) -> Optional[List[Dict[str, Any]]]:
        key = self._make_key("popular_skills", str(days))
        return await self.get(key)

    async def cache_trending_skills(self, skills: List[Dict[str, Any]]) -> bool:
        key = self._make_key("trending_skills")
        return await self.set(key, skills, ttl=self.SEARCH_TTL)

    async def get_cached_trending_skills(self) -> Optional[List[Dict[str, Any]]]:
        key = self._make_key("trending_skills")
        return await self.get(key)

    async def invalidate_all_skill_caches(self) -> int:
        redis = await self._get_redis()
        pattern = self._make_key("skill", "*")
        deleted = 0
        try:
            cursor = 0
            while True:
                cursor, keys = await redis.scan(cursor, match=pattern, count=100)
                if keys:
                    deleted += await redis.delete(*keys)
                if cursor == 0:
                    break
        except Exception:
            pass
        return deleted

    async def invalidate_all_search_caches(self) -> int:
        redis = await self._get_redis()
        pattern = self._make_key("search", "*")
        deleted = 0
        try:
            cursor = 0
            while True:
                cursor, keys = await redis.scan(cursor, match=pattern, count=100)
                if keys:
                    deleted += await redis.delete(*keys)
                if cursor == 0:
                    break
        except Exception:
            pass
        return deleted

    async def get_cache_stats(self) -> Dict[str, Any]:
        redis = await self._get_redis()
        try:
            info = await redis.info("memory")
            keyspace = await redis.info("keyspace")
            return {
                "used_memory_human": info.get("used_memory_human", "0"),
                "used_memory_peak_human": info.get("used_memory_peak_human", "0"),
                "connected_clients": info.get("connected_clients", 0),
                "keyspace": keyspace,
            }
        except Exception:
            return {
                "used_memory_human": "unknown",
                "used_memory_peak_human": "unknown",
                "connected_clients": 0,
                "keyspace": {},
            }

    def _normalize_query(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
    ) -> str:
        parts = [query.lower().strip()]
        if filters:
            sorted_filters = dict(sorted(filters.items()))
            parts.append(json.dumps(sorted_filters, sort_keys=True))
        return ":".join(parts)
from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# Use the modern import path. `from redis import asyncio as aioredis`
# still works in redis 7 but the official home for the async client is
# `redis.asyncio`. The compat alias is kept for downstream code that
# might import `CacheService._redis` and expect the old name.
try:
    from redis.asyncio import Redis as AsyncRedis
    from redis.asyncio import from_url as aioredis_from_url
except ImportError:  # pragma: no cover — fallback for old redis-py builds
    from redis import asyncio as aioredis  # type: ignore[no-redef]

    AsyncRedis = aioredis.Redis  # type: ignore[assignment,misc]
    aioredis_from_url = aioredis.from_url  # type: ignore[assignment]


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
        self._redis: Optional[AsyncRedis] = None
        self._connected = False

    async def _get_redis(self) -> AsyncRedis:
        if self._redis is None or not self._connected:
            # `decode_responses=True` is now safe because we no longer
            # use pickle — values come back as plain strings and `json`
            # turns them into Python objects. The previous combo
            # (pickle + decode_responses=False) required us to call
            # `pickle.loads` on raw bytes, which is the entire reason
            # we were carrying an RCE-shaped dependency in the cache
            # layer. Migrate with care: any pre-existing keys written
            # under the old format will raise on the next read and
            # the `except Exception` swallow in `get` will treat them
            # as cache misses.
            self._redis = aioredis_from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True,
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

    @staticmethod
    def _dumps(value: Any) -> str:
        # The cache is exclusively used for skill dicts, search
        # results, and category lists — all plain JSON. Using `str`
        # for the default makes the contract explicit and avoids
        # silently dropping unknown objects.
        return json.dumps(value, ensure_ascii=False, default=str)

    @staticmethod
    def _loads(raw: str) -> Any:
        return json.loads(raw)

    async def get(self, key: str) -> Optional[Any]:
        redis = await self._get_redis()
        try:
            raw = await redis.get(key)
            if raw is None:
                return None
            return self._loads(raw)
        except Exception:
            # Cache misses shouldn't blow up the request path. We log
            # nothing here because Sentry captures the underlying
            # connection error (e.g. Redis down) at the source.
            # A deserialize error from a stale pickle entry also
            # falls through to a cache miss — exactly the right
            # behavior while we migrate off the old format.
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        redis = await self._get_redis()
        try:
            serialized = self._dumps(value)
            ttl = ttl if ttl is not None else self.default_ttl
            await redis.set(key, serialized, ex=ttl)
            return True
        except Exception:
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

    async def _cache_dashboard_stats(self) -> int:
        """Compute the dashboard rollup once and write it to Redis with a
        short TTL. Returns the number of cache keys written (0 if Redis
        is down — the dashboard endpoint falls back to the DB)."""
        from app.db import async_session_factory
        from app.models.skill import (
            Category,
            Skill,
            SkillComposition,
            SkillRating,
            SkillUsageLog,
            User,
        )
        from sqlalchemy import func, select

        try:
            async with async_session_factory() as db:
                # NOTE: `total_users` and `total_ratings` MUST be scalar
                # subqueries, not joins. Joining User into the Skill
                # outer-join (the natural way to roll everything up in
                # one query) silently turns `count(User.id)` into
                # "users that have at least one usage log" and the
                # same trap applies to `count(SkillRating.id)`. Keep
                # them as independent scalar counts so the cached
                # numbers actually mean "all users" / "all ratings".
                total_users_subq = select(func.count(User.id)).scalar_subquery()
                total_ratings_subq = select(func.count(SkillRating.id)).scalar_subquery()
                total_compositions_subq = select(func.count(SkillComposition.id)).scalar_subquery()
                # Compute "today" in Python so the SQL stays portable
                # between PostgreSQL (prod) and SQLite (tests).
                one_day_ago = datetime.now(timezone.utc) - timedelta(days=1)
                skills_today_subq = (
                    select(func.count(Skill.id))
                    .where(Skill.created_at >= one_day_ago)
                    .scalar_subquery()
                )
                row = (
                    await db.execute(
                        select(
                            func.count(Skill.id),
                            total_users_subq,
                            func.count(SkillUsageLog.id),
                            func.coalesce(func.sum(Skill.download_count), 0),
                            total_ratings_subq,
                            total_compositions_subq,
                            skills_today_subq,
                        )
                        .select_from(Skill)
                        .outerjoin(SkillUsageLog, SkillUsageLog.skill_id == Skill.id)
                        .outerjoin(SkillRating, SkillRating.skill_id == Skill.id)
                    )
                ).one()
                stats = {
                    "total_skills": row[0] or 0,
                    "total_users": row[1] or 0,
                    "total_usage": row[2] or 0,
                    "total_downloads": int(row[3] or 0),
                    "total_ratings": row[4] or 0,
                    "total_compositions": row[5] or 0,
                    "skills_added_today": row[6] or 0,
                    "computed_at": datetime.now(timezone.utc).isoformat(),
                }
            key = self._make_key("dashboard", "stats")
            await self.set(key, stats, ttl=self.SEARCH_TTL)
            return 1
        except Exception:
            return 0

    async def _cache_category_index(self) -> int:
        """Cache the active category list. TTL is hours since categories
        change very rarely (admin-only CRUD)."""
        from app.db import async_session_factory
        from app.models.skill import Category
        from sqlalchemy import select

        try:
            async with async_session_factory() as db:
                rows = (
                    await db.execute(
                        select(Category).where(Category.is_active == True).order_by(Category.sort_order)
                    )
                ).scalars().all()
                cats = [
                    {
                        "id": str(c.id),
                        "name": c.name,
                        "slug": c.slug,
                        "parent_id": str(c.parent_id) if c.parent_id else None,
                        "sort_order": c.sort_order,
                    }
                    for c in rows
                ]
            key = self._make_key("categories", "active")
            await self.set(key, cats, ttl=self.DEFAULT_TTL)
            return 1
        except Exception:
            return 0

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

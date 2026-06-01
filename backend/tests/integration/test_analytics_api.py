import pytest
from httpx import AsyncClient


class TestAnalyticsDashboardAPI:

    @pytest.mark.asyncio
    async def test_dashboard_stats(
        self, test_client: AsyncClient, test_skill: dict, test_user: dict
    ) -> None:
        response = await test_client.get("/api/v1/analytics/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "stats" in data
        assert "popular_skills" in data
        assert "trending_tags" in data

        stats = data["stats"]
        assert stats["total_skills"] >= 1
        assert stats["total_users"] >= 1
        assert "total_categories" in stats
        assert "total_usage" in stats
        assert "total_downloads" in stats
        assert "total_ratings" in stats
        assert "avg_rating" in stats

    @pytest.mark.asyncio
    async def test_dashboard_stats_empty(self, test_client: AsyncClient) -> None:
        response = await test_client.get("/api/v1/analytics/dashboard")
        assert response.status_code == 200
        data = response.json()
        stats = data["stats"]
        assert stats["total_skills"] == 0
        assert stats["total_users"] == 0


class TestAnalyticsSkillsUsageAPI:

    @pytest.mark.asyncio
    async def test_skill_usage_trends(
        self, test_client: AsyncClient, test_skill: dict
    ) -> None:
        response = await test_client.get("/api/v1/analytics/skills/usage")
        assert response.status_code == 200
        data = response.json()
        assert "trend" in data
        assert "period" in data
        assert isinstance(data["trend"], list)

    @pytest.mark.asyncio
    async def test_skill_usage_trends_custom_days(
        self, test_client: AsyncClient
    ) -> None:
        response = await test_client.get(
            "/api/v1/analytics/skills/usage", params={"days": 7}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["period"] == "last_7_days"

    @pytest.mark.asyncio
    async def test_skill_usage_trends_invalid_days(
        self, test_client: AsyncClient
    ) -> None:
        response = await test_client.get(
            "/api/v1/analytics/skills/usage", params={"days": 0}
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_skill_usage_trends_max_days(
        self, test_client: AsyncClient
    ) -> None:
        response = await test_client.get(
            "/api/v1/analytics/skills/usage", params={"days": 365}
        )
        assert response.status_code == 200


class TestAnalyticsPopularSkillsAPI:

    @pytest.mark.asyncio
    async def test_popular_skills(
        self, test_client: AsyncClient, test_skill: dict
    ) -> None:
        response = await test_client.get("/api/v1/analytics/skills/popular")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            skill = data[0]
            assert "id" in skill
            assert "name" in skill
            assert "slug" in skill
            assert "download_count" in skill
            assert "usage_count" in skill
            assert "rating_avg" in skill
            assert "rating_count" in skill

    @pytest.mark.asyncio
    async def test_popular_skills_with_limit(
        self, test_client: AsyncClient, test_skill: dict, test_second_skill: dict
    ) -> None:
        response = await test_client.get(
            "/api/v1/analytics/skills/popular", params={"limit": 1}
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 1


class TestAnalyticsCategoriesDistributionAPI:

    @pytest.mark.asyncio
    async def test_categories_distribution(
        self, test_client: AsyncClient, test_category: dict
    ) -> None:
        response = await test_client.get("/api/v1/analytics/categories/distribution")
        assert response.status_code == 200
        data = response.json()
        assert "distribution" in data
        assert "total" in data
        assert isinstance(data["distribution"], list)


class TestAnalyticsTrendingTagsAPI:

    @pytest.mark.asyncio
    async def test_trending_tags(
        self, test_client: AsyncClient
    ) -> None:
        response = await test_client.get("/api/v1/analytics/tags/trending")
        assert response.status_code == 200
        data = response.json()
        assert "tags" in data
        assert isinstance(data["tags"], list)

    @pytest.mark.asyncio
    async def test_trending_tags_custom_params(
        self, test_client: AsyncClient
    ) -> None:
        response = await test_client.get(
            "/api/v1/analytics/tags/trending",
            params={"days": 7, "limit": 5},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["tags"], list)
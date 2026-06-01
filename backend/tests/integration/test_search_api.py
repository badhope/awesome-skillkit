import pytest
from httpx import AsyncClient


class TestSearchAPI:

    @pytest.mark.asyncio
    async def test_text_search(
        self, test_client: AsyncClient, test_skill: dict
    ) -> None:
        response = await test_client.get(
            "/api/v1/skills/search",
            params={"q": "python"},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_text_search_empty_query(
        self, test_client: AsyncClient
    ) -> None:
        response = await test_client.get(
            "/api/v1/skills/search",
            params={"q": "a"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_text_search_with_limit(
        self, test_client: AsyncClient, test_skill: dict
    ) -> None:
        response = await test_client.get(
            "/api/v1/skills/search",
            params={"q": "python", "limit": 5},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5

    @pytest.mark.asyncio
    async def test_text_search_with_category(
        self, test_client: AsyncClient, test_skill: dict, test_category: dict
    ) -> None:
        response = await test_client.get(
            "/api/v1/skills/search",
            params={
                "q": "python",
                "category_id": test_category["id"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_search_no_results(
        self, test_client: AsyncClient
    ) -> None:
        response = await test_client.get(
            "/api/v1/skills/search",
            params={"q": "xyznonexistent12345"},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_find_similar_skills(
        self, test_client: AsyncClient, test_skill: dict
    ) -> None:
        response = await test_client.get(
            f"/api/v1/skills/{test_skill['slug']}/similar"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_find_similar_skills_nonexistent(
        self, test_client: AsyncClient
    ) -> None:
        response = await test_client.get("/api/v1/skills/nonexistent/similar")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_find_similar_skills_with_limit(
        self, test_client: AsyncClient, test_skill: dict
    ) -> None:
        response = await test_client.get(
            f"/api/v1/skills/{test_skill['slug']}/similar",
            params={"limit": 5},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5
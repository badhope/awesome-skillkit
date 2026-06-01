import pytest
from httpx import AsyncClient


class TestSkillsListAPI:

    @pytest.mark.asyncio
    async def test_list_skills(
        self, test_client: AsyncClient, test_skill: dict
    ) -> None:
        response = await test_client.get("/api/v1/skills")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert data["total"] >= 1
        assert len(data["items"]) >= 1

    @pytest.mark.asyncio
    async def test_list_skills_with_filters(
        self, test_client: AsyncClient, test_skill: dict, test_second_skill: dict
    ) -> None:
        response = await test_client.get(
            "/api/v1/skills",
            params={"complexity": "beginner"},
        )
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["complexity"] == "beginner"

    @pytest.mark.asyncio
    async def test_list_skills_with_category_filter(
        self, test_client: AsyncClient, test_skill: dict, test_category: dict
    ) -> None:
        response = await test_client.get(
            "/api/v1/skills",
            params={"category_slug": test_category["slug"]},
        )
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            if item.get("category"):
                assert item["category"]["slug"] == test_category["slug"]

    @pytest.mark.asyncio
    async def test_list_skills_with_tag_filter(
        self, test_client: AsyncClient, test_skill: dict, test_tag: dict
    ) -> None:
        response = await test_client.get(
            "/api/v1/skills",
            params={"tag": test_tag["name"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1

    @pytest.mark.asyncio
    async def test_list_skills_with_search(
        self, test_client: AsyncClient, test_skill: dict
    ) -> None:
        response = await test_client.get(
            "/api/v1/skills",
            params={"search": "Python"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1

    @pytest.mark.asyncio
    async def test_list_skills_search_no_results(
        self, test_client: AsyncClient
    ) -> None:
        response = await test_client.get(
            "/api/v1/skills",
            params={"search": "xyznonexistent12345"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0

    @pytest.mark.asyncio
    async def test_list_skills_pagination(
        self, test_client: AsyncClient, test_skill: dict, test_second_skill: dict
    ) -> None:
        response = await test_client.get(
            "/api/v1/skills",
            params={"page": 1, "page_size": 1},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 1
        assert len(data["items"]) <= 1

    @pytest.mark.asyncio
    async def test_list_skills_sort_order(
        self, test_client: AsyncClient, test_skill: dict
    ) -> None:
        response = await test_client.get(
            "/api/v1/skills",
            params={"sort_by": "name", "sort_order": "asc"},
        )
        assert response.status_code == 200
        data = response.json()
        names = [item["name"] for item in data["items"]]
        assert names == sorted(names)

    @pytest.mark.asyncio
    async def test_get_skill_by_slug(
        self, test_client: AsyncClient, test_skill: dict
    ) -> None:
        response = await test_client.get(f"/api/v1/skills/{test_skill['slug']}")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == test_skill["name"]
        assert data["slug"] == test_skill["slug"]
        assert data["description"] == test_skill["description"]
        assert "versions" in data
        assert "dependencies" in data

    @pytest.mark.asyncio
    async def test_get_nonexistent_skill(self, test_client: AsyncClient) -> None:
        response = await test_client.get("/api/v1/skills/nonexistent-slug")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_featured_skills(
        self, test_client: AsyncClient, test_skill: dict
    ) -> None:
        response = await test_client.get("/api/v1/skills/featured")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["is_featured"] is True

    @pytest.mark.asyncio
    async def test_get_popular_skills(
        self, test_client: AsyncClient, test_skill: dict
    ) -> None:
        response = await test_client.get("/api/v1/skills/popular")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_trending_skills(
        self, test_client: AsyncClient, test_skill: dict
    ) -> None:
        response = await test_client.get("/api/v1/skills/trending")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestSkillsCreateAPI:

    @pytest.mark.asyncio
    async def test_create_skill_authenticated(
        self, test_client_auth: AsyncClient, test_category: dict
    ) -> None:
        response = await test_client_auth.post(
            "/api/v1/skills",
            json={
                "name": "New Skill",
                "slug": "new-skill",
                "description": "A brand new skill",
                "version": "1.0.0",
                "category_slug": test_category["slug"],
                "complexity": "intermediate",
                "status": "published",
                "license": "MIT",
                "is_public": True,
                "content": {"prompt": "Generate"},
                "metadata": {},
                "tags": ["python", "new"],
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Skill"
        assert data["slug"] == "new-skill"
        assert data["description"] == "A brand new skill"
        assert len(data["tags"]) == 2

    @pytest.mark.asyncio
    async def test_create_skill_unauthenticated(
        self, test_client: AsyncClient, test_category: dict
    ) -> None:
        response = await test_client.post(
            "/api/v1/skills",
            json={
                "name": "Unauth Skill",
                "slug": "unauth-skill",
                "description": "Should fail",
                "version": "1.0.0",
                "category_slug": test_category["slug"],
            },
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_skill_duplicate_slug(
        self, test_client_auth: AsyncClient, test_skill: dict, test_category: dict
    ) -> None:
        response = await test_client_auth.post(
            "/api/v1/skills",
            json={
                "name": "Duplicate",
                "slug": test_skill["slug"],
                "description": "Should fail",
                "version": "1.0.0",
                "category_slug": test_category["slug"],
            },
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]


class TestSkillsUpdateAPI:

    @pytest.mark.asyncio
    async def test_update_skill_as_owner(
        self, test_client_auth: AsyncClient, test_skill: dict
    ) -> None:
        response = await test_client_auth.put(
            f"/api/v1/skills/{test_skill['slug']}",
            json={"description": "Updated description"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"

    @pytest.mark.asyncio
    async def test_update_skill_as_non_owner(
        self, test_client_superuser: AsyncClient, test_skill: dict
    ) -> None:
        response = await test_client_superuser.put(
            f"/api/v1/skills/{test_skill['slug']}",
            json={"description": "Admin updated description"},
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_nonexistent_skill(
        self, test_client_auth: AsyncClient
    ) -> None:
        response = await test_client_auth.put(
            "/api/v1/skills/nonexistent",
            json={"description": "Should fail"},
        )
        assert response.status_code == 404


class TestSkillsDeleteAPI:

    @pytest.mark.asyncio
    async def test_delete_skill_as_owner(
        self, test_client_auth: AsyncClient, test_skill: dict
    ) -> None:
        response = await test_client_auth.delete(
            f"/api/v1/skills/{test_skill['slug']}"
        )
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_nonexistent_skill(
        self, test_client_auth: AsyncClient
    ) -> None:
        response = await test_client_auth.delete("/api/v1/skills/nonexistent")
        assert response.status_code == 404


class TestSkillsVersionAPI:

    @pytest.mark.asyncio
    async def test_get_skill_versions(
        self, test_client: AsyncClient, test_skill: dict, test_skill_version: dict
    ) -> None:
        response = await test_client.get(
            f"/api/v1/skills/{test_skill['slug']}/versions"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_create_skill_version(
        self, test_client_auth: AsyncClient, test_skill: dict
    ) -> None:
        response = await test_client_auth.post(
            f"/api/v1/skills/{test_skill['slug']}/versions",
            json={
                "version": "1.1.0",
                "content": {"prompt": "Updated prompt"},
                "changelog": "Improved prompt",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["version"] == "1.1.0"
        assert data["changelog"] == "Improved prompt"

    @pytest.mark.asyncio
    async def test_create_duplicate_version(
        self, test_client_auth: AsyncClient, test_skill: dict
    ) -> None:
        await test_client_auth.post(
            f"/api/v1/skills/{test_skill['slug']}/versions",
            json={
                "version": "1.0.0",
                "content": {"prompt": "First"},
                "changelog": "First version",
            },
        )
        response = await test_client_auth.post(
            f"/api/v1/skills/{test_skill['slug']}/versions",
            json={
                "version": "1.0.0",
                "content": {"prompt": "Second"},
                "changelog": "Duplicate",
            },
        )
        assert response.status_code == 400
        assert "Version already exists" in response.json()["detail"]


class TestSkillsRatingAPI:

    @pytest.mark.asyncio
    async def test_rate_skill(
        self, test_client_auth: AsyncClient, test_skill: dict
    ) -> None:
        response = await test_client_auth.post(
            f"/api/v1/skills/{test_skill['slug']}/rate",
            json={"rating": 5, "comment": "Excellent!"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["rating"] == 5
        assert data["comment"] == "Excellent!"

    @pytest.mark.asyncio
    async def test_rate_skill_unauthenticated(
        self, test_client: AsyncClient, test_skill: dict
    ) -> None:
        response = await test_client.post(
            f"/api/v1/skills/{test_skill['slug']}/rate",
            json={"rating": 5},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_rate_skill_update_existing(
        self, test_client_auth: AsyncClient, test_skill: dict
    ) -> None:
        await test_client_auth.post(
            f"/api/v1/skills/{test_skill['slug']}/rate",
            json={"rating": 4, "comment": "Good"},
        )
        response = await test_client_auth.post(
            f"/api/v1/skills/{test_skill['slug']}/rate",
            json={"rating": 5, "comment": "Updated to excellent!"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["rating"] == 5


class TestSkillsUsageAPI:

    @pytest.mark.asyncio
    async def test_log_skill_usage(
        self, test_client_auth: AsyncClient, test_skill: dict
    ) -> None:
        response = await test_client_auth.post(
            f"/api/v1/skills/{test_skill['slug']}/use",
            json={"action": "download"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["action"] == "download"

    @pytest.mark.asyncio
    async def test_log_skill_usage_view(
        self, test_client_auth: AsyncClient, test_skill: dict
    ) -> None:
        response = await test_client_auth.post(
            f"/api/v1/skills/{test_skill['slug']}/use",
            json={"action": "view"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["action"] == "view"


class TestSkillsDependencyAPI:

    @pytest.mark.asyncio
    async def test_list_dependencies(
        self, test_client: AsyncClient, test_skill: dict, test_skill_dependency: dict
    ) -> None:
        response = await test_client.get(
            f"/api/v1/skills/{test_skill['slug']}/dependencies"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_add_dependency(
        self, test_client_auth: AsyncClient, test_skill: dict, test_second_skill: dict
    ) -> None:
        response = await test_client_auth.post(
            f"/api/v1/skills/{test_skill['slug']}/dependencies",
            json={
                "depends_on_skill_slug": test_second_skill["slug"],
                "version_constraint": ">=1.0.0",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["version_constraint"] == ">=1.0.0"

    @pytest.mark.asyncio
    async def test_remove_dependency(
        self, test_client_auth: AsyncClient, test_skill: dict, test_skill_dependency: dict
    ) -> None:
        response = await test_client_auth.delete(
            f"/api/v1/skills/{test_skill['slug']}/dependencies/{test_skill_dependency['id']}"
        )
        assert response.status_code == 204
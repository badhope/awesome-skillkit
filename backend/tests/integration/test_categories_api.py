import pytest
from httpx import AsyncClient


class TestCategoriesListAPI:

    @pytest.mark.asyncio
    async def test_list_categories(
        self, test_client: AsyncClient, test_category: dict
    ) -> None:
        response = await test_client.get("/api/v1/categories")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["name"] == test_category["name"]

    @pytest.mark.asyncio
    async def test_list_categories_flat(
        self, test_client: AsyncClient, test_category: dict, test_child_category: dict
    ) -> None:
        response = await test_client.get("/api/v1/categories", params={"flat": True})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2

    @pytest.mark.asyncio
    async def test_list_categories_by_parent(
        self, test_client: AsyncClient, test_category: dict, test_child_category: dict
    ) -> None:
        response = await test_client.get(
            "/api/v1/categories",
            params={"parent_id": test_category["id"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    @pytest.mark.asyncio
    async def test_get_category_tree(
        self, test_client: AsyncClient, test_category: dict, test_child_category: dict
    ) -> None:
        response = await test_client.get("/api/v1/categories/tree")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            root = data[0]
            assert "children" in root
            assert "skill_count" in root

    @pytest.mark.asyncio
    async def test_get_category_by_slug(
        self, test_client: AsyncClient, test_category: dict
    ) -> None:
        response = await test_client.get(
            f"/api/v1/categories/{test_category['slug']}"
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == test_category["name"]
        assert data["slug"] == test_category["slug"]
        assert "skills" in data
        assert "children" in data

    @pytest.mark.asyncio
    async def test_get_nonexistent_category(self, test_client: AsyncClient) -> None:
        response = await test_client.get("/api/v1/categories/nonexistent")
        assert response.status_code == 404


class TestCategoriesCreateAPI:

    @pytest.mark.asyncio
    async def test_create_category_as_superuser(
        self, test_client_superuser: AsyncClient
    ) -> None:
        response = await test_client_superuser.post(
            "/api/v1/categories",
            json={
                "name": "New Category",
                "slug": "new-category",
                "description": "A new test category",
                "icon": "star",
                "sort_order": 0,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Category"
        assert data["slug"] == "new-category"
        assert data["description"] == "A new test category"

    @pytest.mark.asyncio
    async def test_create_category_as_normal_user(
        self, test_client_auth: AsyncClient
    ) -> None:
        response = await test_client_auth.post(
            "/api/v1/categories",
            json={
                "name": "User Category",
                "slug": "user-category",
                "description": "Should fail",
            },
        )
        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_create_category_duplicate_slug(
        self, test_client_superuser: AsyncClient, test_category: dict
    ) -> None:
        response = await test_client_superuser.post(
            "/api/v1/categories",
            json={
                "name": "Duplicate",
                "slug": test_category["slug"],
            },
        )
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_create_category_with_parent(
        self, test_client_superuser: AsyncClient, test_category: dict
    ) -> None:
        response = await test_client_superuser.post(
            "/api/v1/categories",
            json={
                "name": "Child Category",
                "slug": "child-category",
                "description": "A child category",
                "parent_id": test_category["id"],
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["parent_id"] == test_category["id"]

    @pytest.mark.asyncio
    async def test_create_category_invalid_parent(
        self, test_client_superuser: AsyncClient
    ) -> None:
        response = await test_client_superuser.post(
            "/api/v1/categories",
            json={
                "name": "Orphan",
                "slug": "orphan",
                "parent_id": "00000000-0000-0000-0000-000000000099",
            },
        )
        assert response.status_code == 404


class TestCategoriesUpdateAPI:

    @pytest.mark.asyncio
    async def test_update_category(
        self, test_client_superuser: AsyncClient, test_category: dict
    ) -> None:
        response = await test_client_superuser.put(
            f"/api/v1/categories/{test_category['slug']}",
            json={"description": "Updated description"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == "Updated description"

    @pytest.mark.asyncio
    async def test_update_category_self_parent(
        self, test_client_superuser: AsyncClient, test_category: dict
    ) -> None:
        response = await test_client_superuser.put(
            f"/api/v1/categories/{test_category['slug']}",
            json={"parent_id": test_category["id"]},
        )
        assert response.status_code == 400


class TestCategoriesDeleteAPI:

    @pytest.mark.asyncio
    async def test_delete_category(
        self, test_client_superuser: AsyncClient, test_category: dict
    ) -> None:
        response = await test_client_superuser.delete(
            f"/api/v1/categories/{test_category['slug']}"
        )
        assert response.status_code == 204

    @pytest.mark.asyncio
    async def test_delete_category_with_skills(
        self, test_client_superuser: AsyncClient, test_skill: dict
    ) -> None:
        slug = test_skill.get("slug", "")
        import uuid as uuid_lib
        from sqlalchemy import select
        from app.models.skill import Skill, Category

        from sqlalchemy.ext.asyncio import AsyncSession
        from app.db import get_db

        response = await test_client_superuser.delete(
            f"/api/v1/categories/code-generation"
        )
        assert response.status_code == 204
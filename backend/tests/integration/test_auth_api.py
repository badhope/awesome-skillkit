import pytest
from httpx import AsyncClient


class TestAuthAPI:

    @pytest.mark.asyncio
    async def test_register_user(self, test_client: AsyncClient) -> None:
        response = await test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "Str0ngP@ss1",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert data["is_active"] is True
        assert "id" in data

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, test_client: AsyncClient) -> None:
        await test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "dup@example.com",
                "username": "user1",
                "password": "Str0ngP@ss1",
            },
        )
        response = await test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "dup@example.com",
                "username": "user2",
                "password": "Str0ngP@ss2",
            },
        )
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, test_client: AsyncClient) -> None:
        await test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "a@example.com",
                "username": "sameuser",
                "password": "Str0ngP@ss1",
            },
        )
        response = await test_client.post(
            "/api/v1/auth/register",
            json={
                "email": "b@example.com",
                "username": "sameuser",
                "password": "Str0ngP@ss2",
            },
        )
        assert response.status_code == 400
        assert "Username already taken" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_success(self, test_client: AsyncClient, test_user: dict) -> None:
        response = await test_client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user["username"],
                "password": test_user["password"],
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self, test_client: AsyncClient) -> None:
        response = await test_client.post(
            "/api/v1/auth/login",
            json={
                "username": "nonexistent",
                "password": "WrongPass1!",
            },
        )
        assert response.status_code == 401
        assert "Invalid username or password" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_login_wrong_password(self, test_client: AsyncClient, test_user: dict) -> None:
        response = await test_client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user["username"],
                "password": "WrongPassword1!",
            },
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_refresh_token(self, test_client: AsyncClient, test_user: dict) -> None:
        login_response = await test_client.post(
            "/api/v1/auth/login",
            json={
                "username": test_user["username"],
                "password": test_user["password"],
            },
        )
        refresh_token = login_response.json()["refresh_token"]

        response = await test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_refresh_with_invalid_token(self, test_client: AsyncClient) -> None:
        response = await test_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid-refresh-token"},
        )
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_get_me(self, test_client_auth: AsyncClient, test_user: dict) -> None:
        response = await test_client_auth.get("/api/v1/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == test_user["email"]
        assert data["username"] == test_user["username"]

    @pytest.mark.asyncio
    async def test_get_me_unauthenticated(self, test_client: AsyncClient) -> None:
        response = await test_client.get("/api/v1/auth/me")
        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_change_password(
        self, test_client_auth: AsyncClient, test_user: dict
    ) -> None:
        response = await test_client_auth.put(
            "/api/v1/auth/me/password",
            json={
                "current_password": test_user["password"],
                "new_password": "NewStr0ngP@ss1!",
            },
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Password changed successfully"

    @pytest.mark.asyncio
    async def test_change_password_wrong_current(
        self, test_client_auth: AsyncClient
    ) -> None:
        response = await test_client_auth.put(
            "/api/v1/auth/me/password",
            json={
                "current_password": "WrongCurrent1!",
                "new_password": "NewStr0ngP@ss1!",
            },
        )
        assert response.status_code == 400
        assert "Current password is incorrect" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_update_current_user(
        self, test_client_auth: AsyncClient, test_user: dict
    ) -> None:
        response = await test_client_auth.put(
            "/api/v1/auth/me",
            json={"full_name": "Updated Name"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "Updated Name"

    @pytest.mark.asyncio
    async def test_update_current_user_email_conflict(
        self, test_client_auth: AsyncClient, test_superuser: dict
    ) -> None:
        response = await test_client_auth.put(
            "/api/v1/auth/me",
            json={"email": test_superuser["email"]},
        )
        assert response.status_code == 400
        assert "Email already in use" in response.json()["detail"]

"""Tests for the security headers middleware and the startup secret validator."""
from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient


@pytest.mark.asyncio
async def test_security_headers_attached_to_responses():
    """Every response gets the OWASP-recommended security headers."""
    from fastapi import FastAPI

    from app.middleware.security_headers import (
        DEFAULT_SECURITY_HEADERS,
        SecurityHeadersMiddleware,
    )

    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware)

    @app.get("/probe")
    async def probe():
        return {"ok": True}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/probe")

    assert response.status_code == 200
    for header, expected in DEFAULT_SECURITY_HEADERS.items():
        assert response.headers.get(header) == expected, (
            f"Missing or wrong header {header}: {response.headers.get(header)!r}"
        )


@pytest.mark.asyncio
async def test_security_headers_strip_x_powered_by():
    """X-Powered-By is removed to avoid fingerprinting."""
    from fastapi import FastAPI

    from app.middleware.security_headers import SecurityHeadersMiddleware

    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware)

    @app.get("/probe")
    async def probe():
        return {"ok": True}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/probe")

    assert "x-powered-by" not in {k.lower() for k in response.headers.keys()}


@pytest.mark.asyncio
async def test_security_headers_preserve_existing_headers():
    """If a downstream handler already set a header, we don't overwrite it."""
    from fastapi import FastAPI

    from app.middleware.security_headers import SecurityHeadersMiddleware

    app = FastAPI()
    app.add_middleware(SecurityHeadersMiddleware)

    @app.get("/probe")
    async def probe():
        from fastapi.responses import JSONResponse
        return JSONResponse(
            {"ok": True},
            headers={"X-Frame-Options": "SAMEORIGIN"},
        )

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/probe")

    assert response.headers["X-Frame-Options"] == "SAMEORIGIN"


def test_production_rejects_missing_jwt_secret():
    """Production must fail fast without JWT_SECRET_KEY."""
    from pydantic import ValidationError

    from app.core.config import Settings

    with pytest.raises(ValidationError) as exc_info:
        Settings(
            DEBUG=False,
            JWT_SECRET_KEY=None,
            BACKEND_CORS_ORIGINS=["http://localhost:3000"],
        )

    assert "JWT_SECRET_KEY" in str(exc_info.value)


def test_production_rejects_short_jwt_secret():
    """JWT_SECRET_KEY shorter than 32 chars is rejected in production."""
    from pydantic import ValidationError

    from app.core.config import Settings

    with pytest.raises(ValidationError) as exc_info:
        Settings(
            DEBUG=False,
            JWT_SECRET_KEY="short",
            BACKEND_CORS_ORIGINS=["http://localhost:3000"],
        )

    assert "32 characters" in str(exc_info.value)


def test_production_rejects_known_weak_jwt_secret():
    """The well-known weak defaults are rejected in production."""
    from pydantic import ValidationError

    from app.core.config import Settings

    with pytest.raises(ValidationError) as exc_info:
        Settings(
            DEBUG=False,
            JWT_SECRET_KEY="your-super-secret-key-change-in-production",
            BACKEND_CORS_ORIGINS=["http://localhost:3000"],
        )

    msg = str(exc_info.value).lower()
    assert "weak" in msg or "default" in msg


def test_debug_generates_ephemeral_jwt_secret():
    """In DEBUG mode, a missing JWT_SECRET_KEY gets a random 64+ char one."""
    from app.core.config import Settings

    s = Settings(
        DEBUG=True,
        BACKEND_CORS_ORIGINS=["http://localhost:3000"],
    )
    assert s.JWT_SECRET_KEY is not None
    assert len(s.JWT_SECRET_KEY) >= 32


def test_production_accepts_strong_jwt_secret():
    """A 32+ char secret that is not on the weak denylist works."""
    from app.core.config import Settings

    s = Settings(
        DEBUG=False,
        JWT_SECRET_KEY="a" * 32 + "very-strong-and-not-in-denylist-xyz123",
        BACKEND_CORS_ORIGINS=["http://localhost:3000"],
    )
    assert len(s.JWT_SECRET_KEY) >= 32


def test_seed_module_does_not_hardcode_password():
    """The seed module no longer references the old hardcoded value."""
    with open("/workspace/modern_skill_system/backend/app/core/seed.py") as f:
        content = f.read()
    assert "Admin1234" not in content
    assert 'ADMIN_PASSWORD = "Admin1234"' not in content
    assert 'os.environ.get("ADMIN_PASSWORD")' in content


def test_alembic_migration_does_not_hardcode_admin():
    """The migration no longer ships with a hardcoded admin password."""
    with open(
        "/workspace/modern_skill_system/backend/alembic/versions/0001_initial.py"
    ) as f:
        content = f.read()
    assert "admin123" not in content
    assert "SEED_ADMIN" not in content


def test_docker_compose_requires_jwt_and_admin_password():
    """docker-compose.yml refuses to start without the critical secrets."""
    with open("/workspace/modern_skill_system/docker-compose.yml") as f:
        content = f.read()
    # Mandatory env interpolation
    assert "${JWT_SECRET_KEY:?JWT_SECRET_KEY is required" in content
    assert "${ADMIN_PASSWORD:?ADMIN_PASSWORD is required" in content
    assert "${POSTGRES_PASSWORD:?POSTGRES_PASSWORD is required" in content
    # No insecure default fallbacks
    assert ":-change-this-in-production" not in content
    assert "skill_pass" not in content
    assert ":-your-super-secret-key" not in content


def test_env_example_documents_required_secrets():
    """.env.example explains how to generate the required secrets."""
    with open("/workspace/modern_skill_system/.env.example") as f:
        content = f.read()
    assert "openssl rand -hex 32" in content
    assert "openssl rand -base64 18" in content
    assert "JWT_SECRET_KEY=\"\";" in content or "JWT_SECRET_KEY=\"\"" in content
    assert "ADMIN_PASSWORD=\"\";" in content or "ADMIN_PASSWORD=\"\"" in content

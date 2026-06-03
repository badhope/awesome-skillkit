from fastapi import APIRouter

# /v1 is fixed in the URL prefix (see main.py). When we eventually cut
# v2 we should either version-by-header (Accept: application/vnd...v2+json)
# or keep stacking include_router calls with explicit prefix overrides.
from app.api.v1 import analytics, auth, categories, compositions, dashboard, skills, tags, users

api_router = APIRouter()

api_router.include_router(
    auth.router,
    prefix="/auth",
    tags=["auth"],
)

api_router.include_router(
    skills.router,
    prefix="/skills",
    tags=["skills"],
)

api_router.include_router(
    categories.router,
    prefix="/categories",
    tags=["categories"],
)

api_router.include_router(
    tags.router,
    prefix="/tags",
    tags=["tags"],
)

api_router.include_router(
    users.router,
    prefix="/users",
    tags=["users"],
)

api_router.include_router(
    analytics.router,
    prefix="/analytics",
    tags=["analytics"],
)

api_router.include_router(
    compositions.router,
    prefix="/compositions",
    tags=["compositions"],
)

api_router.include_router(
    dashboard.router,
    prefix="/dashboard",
    tags=["dashboard"],
)

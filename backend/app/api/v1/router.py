from fastapi import APIRouter

from app.api.v1 import auth, categories, compositions, skills, tags, users, analytics

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
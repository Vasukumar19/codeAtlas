"""Version-one API route registration."""

from fastapi import APIRouter

from app.api.endpoints import exploration, health, intelligence, repositories

api_router = APIRouter()
api_router.include_router(health.router, tags=["system"])
api_router.include_router(repositories.router, prefix="/repositories", tags=["Repository"])
api_router.include_router(intelligence.router, prefix="/intelligence", tags=["Intelligence"])
api_router.include_router(exploration.router, prefix="/repositories", tags=["Exploration"])

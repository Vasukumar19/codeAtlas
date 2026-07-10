"""Version-one API route registration."""

from fastapi import APIRouter

from app.api.endpoints import health
from app.api.endpoints import repositories

api_router = APIRouter()
api_router.include_router(health.router, tags=["system"])
api_router.include_router(repositories.router, prefix="/repositories", tags=["Repository"])

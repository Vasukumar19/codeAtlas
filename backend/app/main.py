"""FastAPI application entry point for the CodeAtlas API."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.core.middleware import RequestIDMiddleware
from app.core.exceptions import setup_exception_handlers

from app.db.base import Base
from app.api.deps import get_db
from app.db.session import engine
from app.intelligence.models.registry import ModelRegistry
from app.intelligence.models.gemini import GeminiProvider
from app.intelligence.models.openai import OpenAIProvider

@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """Manage application resources without opening database connections eagerly."""
    ModelRegistry.register("Gemini", GeminiProvider())
    ModelRegistry.register("OpenAI", OpenAIProvider())
    async with engine.begin() as conn:
        from sqlalchemy import text
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title=settings.project_name,
    version=settings.version,
    openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIDMiddleware)
setup_exception_handlers(app)
app.include_router(api_router, prefix=settings.api_v1_prefix)

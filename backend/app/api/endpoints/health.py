"""Public Milestone 1 API endpoints."""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from app.core.config import settings

router = APIRouter()


class ApiResponse(BaseModel):
    """Consistent response envelope required by the API specification."""

    status: str = "success"
    message: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    request_id: str
    data: dict[str, Any] | None = None
    errors: list[dict[str, Any]] | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


def response(
    request: Request, message: str, data: dict[str, Any] | None = None
) -> ApiResponse:
    """Create a response envelope bound to the request correlation identifier."""
    return ApiResponse(message=message, request_id=request.state.request_id, data=data)


@router.get("/", response_model=ApiResponse, summary="API root")
async def root(request: Request) -> ApiResponse:
    """Return a discoverable entry point for API clients."""
    return response(request, "Welcome to CodeAtlas API")


@router.get("/health", response_model=ApiResponse, summary="Service health")
async def health_check(request: Request) -> ApiResponse:
    """Report that the web service is available without querying business data."""
    return response(request, "Service is healthy", {"service": "codeatlas"})


@router.get("/version", response_model=ApiResponse, summary="Application version")
async def version(request: Request) -> ApiResponse:
    """Return the current application version."""
    return response(request, "Version retrieved", {"version": settings.version})

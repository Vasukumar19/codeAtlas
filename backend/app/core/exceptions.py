from fastapi import Request, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from app.api.endpoints.health import ApiResponse
from app.core.logger import get_logger

logger = get_logger(__name__)

def setup_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        response = ApiResponse(
            status="error",
            message=str(exc.detail),
            request_id=request_id,
            errors=[{"detail": exc.detail, "status_code": exc.status_code}]
        )
        return JSONResponse(status_code=exc.status_code, content=response.model_dump(mode='json'))

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        errors = [{"loc": err["loc"], "msg": err["msg"], "type": err["type"]} for err in exc.errors()]
        response = ApiResponse(
            status="error",
            message="Validation Error",
            request_id=request_id,
            errors=errors
        )
        return JSONResponse(status_code=422, content=response.model_dump(mode='json'))

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        logger.error("Database Error", request_id=request_id, error=str(exc))
        response = ApiResponse(
            status="error",
            message="Database Error",
            request_id=request_id,
            errors=[{"detail": "Internal database error"}]
        )
        return JSONResponse(status_code=500, content=response.model_dump(mode='json'))

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        request_id = getattr(request.state, "request_id", "unknown")
        logger.error("Unhandled Exception", request_id=request_id, error=str(exc))
        response = ApiResponse(
            status="error",
            message="Internal Server Error",
            request_id=request_id,
            errors=[{"detail": "An unexpected error occurred"}]
        )
        return JSONResponse(status_code=500, content=response.model_dump(mode='json'))

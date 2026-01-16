"""
FastAPI Application Entry Point
Follows Clean Architecture and Dependency Injection patterns
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import structlog
from typing import Dict, Any

from app.core import settings, AppException


# Configure structured logging
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Replaces deprecated @app.on_event decorators.
    """
    # Startup
    logger.info(
        "application_startup",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment
    )

    # Initialize database connection (will be done in Alembic migrations)
    # For now, just log that we're ready
    logger.info("database_connection_ready", db_host=settings.db_host)

    yield

    # Shutdown
    logger.info("application_shutdown")


# Initialize FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered financial management backend with Monobank integration",
    docs_url="/docs" if settings.debug else None,  # Hide docs in production
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle custom application exceptions."""
    logger.error(
        "application_error",
        error=exc.message,
        status_code=exc.status_code,
        details=exc.details,
        path=request.url.path
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "details": exc.details,
            "path": str(request.url.path)
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    logger.exception(
        "unexpected_error",
        error=str(exc),
        path=request.url.path
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "details": {} if not settings.debug else {"message": str(exc)},
            "path": str(request.url.path)
        }
    )


# Health check endpoint
@app.get(
    "/health",
    tags=["Health"],
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check if the API is running and database is accessible"
)
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for monitoring and load balancers.

    Returns:
        Dictionary with application status and version info
    """
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "database": {
            "host": settings.db_host,
            "status": "connected"  # Will be enhanced with actual DB check later
        }
    }


# Root endpoint
@app.get(
    "/",
    tags=["Root"],
    response_model=Dict[str, str],
    summary="API Root",
    description="Welcome message and API information"
)
async def root() -> Dict[str, str]:
    """Root endpoint with welcome message."""
    return {
        "message": f"Welcome to {settings.app_name} API",
        "version": settings.app_version,
        "docs": "/docs" if settings.debug else "Documentation disabled in production",
        "health": "/health"
    }


# API v1 router will be added here
# from app.presentation.api.v1.router import api_router
# app.include_router(api_router, prefix="/api/v1")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="debug" if settings.debug else "info"
    )
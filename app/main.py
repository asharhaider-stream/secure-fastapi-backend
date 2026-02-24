"""
main.py - Application Entry Point and Composition Root
"""

from contextlib import asynccontextmanager
import structlog
from fastapi import FastAPI
from app.config import settings
from app.logging_config import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger = setup_logging()
    logger.info(
        "application_starting",
        app_name=settings.app_name,
        version=settings.app_version,
        environment=settings.environment,
    )
    yield
    logger.info("application_shutdown", app_name=settings.app_name)


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    lifespan=lifespan,
)


@app.get("/health", tags=["System"])
async def health_check():
    logger = structlog.get_logger("app.health")
    logger.info("health_check_called")
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
    }
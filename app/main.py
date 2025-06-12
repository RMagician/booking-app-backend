"""
Main application module
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import connect_to_mongodb, close_mongodb_connection
from app.routes import health_router


def create_application() -> FastAPI:
    """Create and configure the FastAPI application"""
    settings = get_settings()

    application = FastAPI(
        title="Booking App API",
        description="API for booking application",
        version="0.1.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    # Set up CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, replace with specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add startup and shutdown events
    application.add_event_handler("startup", connect_to_mongodb)
    application.add_event_handler("shutdown", close_mongodb_connection)

    # Add routers with prefix
    application.include_router(health_router, prefix=settings.API_PREFIX)

    return application


app = create_application()

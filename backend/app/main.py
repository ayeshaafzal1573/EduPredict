"""
EduPredict FastAPI Application
Main entry point with CORS, middleware, and route registration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection, db_manager
from app.api.v1.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup & shutdown events"""
    await connect_to_mongo()
    yield
    await close_mongo_connection()


# Create FastAPI app
app = FastAPI(
    title="EduPredict API",
    description="AI-Powered Student Performance & Dropout Prediction System",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Middleware: CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware: Trusted Hosts
if settings.ALLOWED_HOSTS:
    app.add_middleware(
        TrustedHostMiddleware,  # type: ignore
        allowed_hosts=settings.ALLOWED_HOSTS,
    )

# Register routers
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["System"])
async def root():
    return {
        "message": "Welcome to EduPredict API 🚀",
        "version": "1.0.0",
        "docs": "/api/docs"
    }


@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy", "service": "EduPredict API"}

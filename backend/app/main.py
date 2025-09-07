from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from loguru import logger
from app.core.config import settings
from app.core.database import connect_to_mongo, close_mongo_connection
from app.api.v1.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup & shutdown events"""
    try:
        connected = await connect_to_mongo()
        if connected:
            logger.info("✅ MongoDB connected successfully")
        else:
            logger.warning("⚠️ MongoDB connection failed, running in fallback mode")
        yield
        
    except Exception as e:
        logger.error(f"Lifespan error: {e}")
        # Don't raise to prevent startup failure
        yield


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
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS,
    )

# Register routers
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["System"])
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to EduPredict API 🚀",
        "version": "1.0.0",
        "docs": "/api/docs"
    }


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "EduPredict API"}

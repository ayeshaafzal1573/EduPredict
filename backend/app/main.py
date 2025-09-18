from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
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
        yield
    finally:
        await close_mongo_connection()

app = FastAPI(
    title="EduPredict API",
    description="AI-Powered Student Performance & Dropout Prediction System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS + ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(api_router, prefix="/api/v1")

@app.get("/", tags=["System"])
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to EduPredict API 🚀",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "service": "EduPredict API",
        "timestamp": "2024-01-15T10:00:00Z"
    }

@app.exception_handler(404)
async def not_found_handler(request, exc):
    return HTTPException(status_code=404, detail="Endpoint not found")

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return HTTPException(status_code=500, detail="Internal server error")
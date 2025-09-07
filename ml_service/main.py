from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
import uvicorn
import logging
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional
import os
from dotenv import load_dotenv

# Import our modules
from app.core.config import settings
from app.core.security import verify_token
from app.api.v1.endpoints import symptoms, drug_interactions, compliance, forecasting, recommendations
from app.core.monitoring import setup_monitoring
from app.core.logging import setup_logging

# Load environment variables
load_dotenv()

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Security
security = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting ML Service...")
    setup_monitoring()
    logger.info("ML Service started successfully")

    yield

    # Shutdown
    logger.info("Shutting down ML Service...")

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="CDSS ML Service",
        description="AI-Driven Clinical Decision Support System - Machine Learning Service",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(
        symptoms.router,
        prefix="/api/v1",
        tags=["symptoms"]
    )

    app.include_router(
        drug_interactions.router,
        prefix="/api/v1",
        tags=["drug_interactions"]
    )

    app.include_router(
        compliance.router,
        prefix="/api/v1",
        tags=["compliance"]
    )

    app.include_router(
        forecasting.router,
        prefix="/api/v1",
        tags=["forecasting"]
    )

    app.include_router(
        recommendations.router,
        prefix="/api/v1",
        tags=["recommendations"]
    )

    # Health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check():
        return {"status": "healthy", "service": "cdss-ml-service"}

    # Root endpoint
    @app.get("/", tags=["root"])
    async def root():
        return {
            "message": "CDSS ML Service",
            "version": "1.0.0",
            "docs": "/docs"
        }

    return app

# Create the app instance
app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )


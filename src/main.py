"""
Multi-Agent AI System - Main Application Entry Point
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from config.settings import settings
from core.database import create_tables, get_db
from api.routes import projects, agents, tasks, debug
from core.system_manager import SystemManager
from utils.logging_config import setup_logging


# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Multi-Agent AI System...")
    
    # Initialize database
    create_tables()
    logger.info("Database tables created")
    
    # Initialize system manager
    system_manager = SystemManager()
    await system_manager.initialize()
    app.state.system_manager = system_manager
    logger.info("System manager initialized")
    
    yield
    
    # Cleanup
    logger.info("Shutting down Multi-Agent AI System...")
    await system_manager.shutdown()
    logger.info("System shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Multi-Agent AI System",
    description="A comprehensive multi-agent AI system with hive collective intelligence",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.system.environment
    }


# System status endpoint
@app.get("/status")
async def system_status():
    """Get system status"""
    try:
        system_manager = app.state.system_manager
        status = await system_manager.get_status()
        return status
    except Exception as e:
        logger.error(f"Error getting system status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system status")


# Include API routes
app.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])
app.include_router(agents.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(debug.router, prefix="/api/v1/debug", tags=["debug"])


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.system.api_host,
        port=settings.system.api_port,
        reload=settings.system.debug,
        log_level=settings.monitoring.log_level.lower()
    )


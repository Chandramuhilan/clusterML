"""ClusterML Master Node - Main Entry Point."""

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("Starting ClusterML Master...")
    # TODO: Initialize scheduler, database connections, etc.
    yield
    logger.info("Shutting down ClusterML Master...")
    # TODO: Cleanup resources


app = FastAPI(
    title="ClusterML Master",
    description="Distributed ML Job Scheduling Platform",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "ClusterML Master",
        "version": "0.1.0",
        "docs": "/docs"
    }


# TODO: Import and include routers
# from app.api import jobs, nodes, auth
# app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["jobs"])
# app.include_router(nodes.router, prefix="/api/v1/nodes", tags=["nodes"])
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8080)),
        reload=os.getenv("DEV_MODE", "false").lower() == "true"
    )

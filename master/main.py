"""ClusterML Master Node - Main Entry Point.

Starts the FastAPI server and wires together storage, node management,
job management, scheduling, and REST API routes.
"""

import logging
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure project root is on sys.path so `core.*` and `master.*` imports work
# when running with `python main.py` from the master/ directory.
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from core.config.settings import get_settings  # noqa: E402
from master.app.storage import get_store  # noqa: E402
from master.app.nodes import NodeManager  # noqa: E402
from master.app.jobs import JobManager  # noqa: E402
from master.app.scheduler import Scheduler  # noqa: E402
from master.app.api import jobs as jobs_api, nodes as nodes_api  # noqa: E402

# ── Settings & Logging ──────────────────────────────────────────────────────
settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# ── Globals initialised in lifespan ─────────────────────────────────────────
scheduler: Scheduler | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler – boot and teardown."""
    global scheduler

    logger.info("Starting ClusterML Master...")

    # 1. Storage
    store = get_store()
    logger.info(f"Storage backend: {settings.storage_backend}")

    # 2. Managers
    node_manager = NodeManager(store, node_timeout_seconds=settings.node_timeout_seconds)
    job_manager = JobManager(store)

    # 3. Scheduler
    scheduler = Scheduler(
        store=store,
        job_manager=job_manager,
        node_manager=node_manager,
        interval_seconds=settings.scheduler_interval_seconds,
    )
    await scheduler.start()

    # 4. Inject into API routers
    jobs_api.init(job_manager, scheduler)
    nodes_api.init(node_manager, store)

    logger.info("ClusterML Master is ready ✓")
    yield

    # Teardown
    logger.info("Shutting down ClusterML Master...")
    if scheduler:
        await scheduler.stop()
    logger.info("Shutdown complete")


# ── FastAPI App ─────────────────────────────────────────────────────────────

app = FastAPI(
    title="ClusterML Master",
    description="Distributed ML Job Scheduling & Orchestration Platform",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── API Routers ─────────────────────────────────────────────────────────────
app.include_router(jobs_api.router, prefix="/api/v1/jobs", tags=["jobs"])
app.include_router(nodes_api.router, prefix="/api/v1/nodes", tags=["nodes"])


# ── Root Endpoints ──────────────────────────────────────────────────────────

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "scheduler": scheduler is not None}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "ClusterML Master",
        "version": "0.1.0",
        "docs": "/docs",
        "endpoints": {
            "jobs": "/api/v1/jobs",
            "nodes": "/api/v1/nodes",
            "cluster_status": "/api/v1/nodes/status",
            "health": "/health",
        },
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=settings.master_host,
        port=settings.master_port,
        reload=settings.dev_mode,
    )

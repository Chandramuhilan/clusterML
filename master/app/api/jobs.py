"""Jobs API - REST endpoints for job CRUD and lifecycle management.

Endpoints:
    POST   /api/v1/jobs          - Submit a new job
    GET    /api/v1/jobs          - List jobs (with filters)
    GET    /api/v1/jobs/{id}     - Get job details
    PUT    /api/v1/jobs/{id}     - Update job (status, result, logs)
    DELETE /api/v1/jobs/{id}     - Cancel a job
    GET    /api/v1/jobs/{id}/logs - Get job logs
    GET    /api/v1/jobs/stats    - Job statistics
"""

import logging
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, status

from core.protocols.models import Job, JobCreate, JobStatus, JobUpdate

logger = logging.getLogger(__name__)

router = APIRouter()

# These will be injected at startup (see main.py)
_job_manager = None
_scheduler = None


def init(job_manager, scheduler):
    """Inject dependencies. Called at application startup."""
    global _job_manager, _scheduler
    _job_manager = job_manager
    _scheduler = scheduler


@router.post("", response_model=Job, status_code=status.HTTP_201_CREATED)
async def submit_job(job_create: JobCreate):
    """Submit a new job for scheduling."""
    job = _job_manager.create(job_create)
    # Trigger the scheduler immediately so the job is matched to a node
    _scheduler.trigger()
    return job


@router.get("/stats", response_model=Dict[str, int])
async def job_stats():
    """Get aggregated job statistics by status."""
    return _job_manager.get_stats()


@router.get("", response_model=List[Job])
async def list_jobs(
    status_filter: Optional[JobStatus] = Query(None, alias="status"),
    label: Optional[str] = Query(None, description="Filter by label, e.g. team=ml"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
):
    """List jobs with optional filtering."""
    return _job_manager.list(status=status_filter, label=label, limit=limit, offset=offset)


@router.get("/{job_id}", response_model=Job)
async def get_job(job_id: str):
    """Get a single job by ID."""
    job = _job_manager.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return job


@router.put("/{job_id}", response_model=Job)
async def update_job(job_id: str, update: JobUpdate):
    """Update a job's status, result, or logs.

    Typically called by worker agents to report progress/completion.
    """
    job = _job_manager.update(job_id, update)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return job


@router.delete("/{job_id}", response_model=Job)
async def cancel_job(job_id: str):
    """Cancel a job. No-op if already in a terminal state."""
    job = _job_manager.cancel(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return job


@router.get("/{job_id}/logs")
async def get_job_logs(job_id: str):
    """Retrieve logs for a job."""
    job = _job_manager.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return {"job_id": job_id, "logs": job.logs or ""}

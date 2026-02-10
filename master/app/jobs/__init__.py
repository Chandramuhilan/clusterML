"""Job Management - CRUD and lifecycle operations for jobs."""

import logging
from datetime import datetime
from typing import Dict, List, Optional

from core.protocols.models import (
    Job,
    JobCreate,
    JobStatus,
    JobUpdate,
)
from master.app.storage import InMemoryStore

logger = logging.getLogger(__name__)


class JobManager:
    """Manages job lifecycle: create, update status, cancel, query."""

    def __init__(self, store: InMemoryStore):
        self.store = store

    def create(self, job_create: JobCreate) -> Job:
        """Create and enqueue a new job."""
        job = self.store.create_job(job_create)
        # Immediately move to QUEUED
        self.store.update_job(job.id, status=JobStatus.QUEUED)
        job.status = JobStatus.QUEUED
        logger.info(f"Job {job.id} ({job.name}) → QUEUED")
        return job

    def get(self, job_id: str) -> Optional[Job]:
        """Get a job by ID."""
        return self.store.get_job(job_id)

    def list(
        self,
        status: Optional[JobStatus] = None,
        label: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Job]:
        """List jobs with optional filtering."""
        return self.store.list_jobs(status=status, label=label, limit=limit, offset=offset)

    def update(self, job_id: str, update: JobUpdate) -> Optional[Job]:
        """Apply an update to a job."""
        kwargs: Dict = {}
        if update.status is not None:
            kwargs["status"] = update.status
            if update.status == JobStatus.RUNNING:
                kwargs["started_at"] = datetime.utcnow()
            elif update.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
                kwargs["completed_at"] = datetime.utcnow()
        if update.result is not None:
            kwargs["result"] = update.result
        if update.logs is not None:
            kwargs["logs"] = update.logs

        job = self.store.update_job(job_id, **kwargs)
        if job:
            logger.info(f"Job {job_id} updated: {kwargs}")
        return job

    def cancel(self, job_id: str) -> Optional[Job]:
        """Cancel a job if it hasn't completed."""
        job = self.store.get_job(job_id)
        if not job:
            return None
        if job.status in (JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED):
            logger.warning(f"Cannot cancel job {job_id} in terminal state {job.status}")
            return job  # Already terminal

        return self.store.update_job(
            job_id,
            status=JobStatus.CANCELLED,
            completed_at=datetime.utcnow(),
        )

    def mark_running(self, job_id: str, worker_id: str) -> Optional[Job]:
        """Transition a job to RUNNING on a specific worker."""
        return self.store.update_job(
            job_id,
            status=JobStatus.RUNNING,
            worker_id=worker_id,
            started_at=datetime.utcnow(),
        )

    def mark_completed(self, job_id: str, result: Optional[Dict] = None) -> Optional[Job]:
        """Transition a job to COMPLETED."""
        return self.store.update_job(
            job_id,
            status=JobStatus.COMPLETED,
            completed_at=datetime.utcnow(),
            result=result or {},
        )

    def mark_failed(self, job_id: str, error: str) -> Optional[Job]:
        """Transition a job to FAILED."""
        return self.store.update_job(
            job_id,
            status=JobStatus.FAILED,
            completed_at=datetime.utcnow(),
            error=error,
        )

    def get_stats(self) -> Dict[str, int]:
        """Get job count by status."""
        return self.store.count_jobs_by_status()

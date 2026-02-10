"""In-Memory Storage Layer.

Thread-safe in-memory storage for jobs and nodes.
This is the default backend for development / single-instance deployments.
For production, swap with a database-backed implementation that exposes
the same interface.
"""

import logging
import threading
from datetime import datetime
from typing import Dict, List, Optional

from core.protocols.models import (
    Job,
    JobCreate,
    JobStatus,
    Node,
    NodeRegister,
    NodeStatus,
)

logger = logging.getLogger(__name__)


class InMemoryStore:
    """Thread-safe in-memory store for jobs and nodes."""

    def __init__(self) -> None:
        self._jobs: Dict[str, Job] = {}
        self._nodes: Dict[str, Node] = {}
        self._lock = threading.Lock()

    # ── Job Operations ──────────────────────────────────────────────────

    def create_job(self, job_create: JobCreate) -> Job:
        """Create a new job and add to store."""
        job = Job(
            name=job_create.name,
            labels=job_create.labels,
            spec=job_create.spec,
            status=JobStatus.PENDING,
        )
        with self._lock:
            self._jobs[job.id] = job
        logger.info(f"Created job {job.id} ({job.name})")
        return job

    def get_job(self, job_id: str) -> Optional[Job]:
        """Get job by ID."""
        return self._jobs.get(job_id)

    def list_jobs(
        self,
        status: Optional[JobStatus] = None,
        label: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Job]:
        """List jobs with optional filtering."""
        jobs = list(self._jobs.values())

        if status:
            jobs = [j for j in jobs if j.status == status]

        if label:
            key, _, value = label.partition("=")
            if value:
                jobs = [j for j in jobs if j.labels.get(key) == value]
            else:
                jobs = [j for j in jobs if key in j.labels]

        # Sort by created_at descending
        jobs.sort(key=lambda j: j.created_at, reverse=True)
        return jobs[offset : offset + limit]

    def update_job(self, job_id: str, **kwargs) -> Optional[Job]:
        """Update job fields."""
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return None
            for key, value in kwargs.items():
                if hasattr(job, key):
                    setattr(job, key, value)
            self._jobs[job_id] = job
        return job

    def get_pending_jobs(self) -> List[Job]:
        """Get all jobs in PENDING status, ordered by creation time."""
        return sorted(
            [j for j in self._jobs.values() if j.status == JobStatus.PENDING],
            key=lambda j: j.created_at,
        )

    def get_running_jobs(self) -> List[Job]:
        """Get all currently running jobs."""
        return [j for j in self._jobs.values() if j.status == JobStatus.RUNNING]

    def count_jobs_by_status(self) -> Dict[str, int]:
        """Return a count of jobs grouped by status."""
        counts: Dict[str, int] = {}
        for job in self._jobs.values():
            counts[job.status.value] = counts.get(job.status.value, 0) + 1
        return counts

    # ── Node Operations ─────────────────────────────────────────────────

    def register_node(self, registration: NodeRegister) -> Node:
        """Register a new worker node."""
        # Check if node with same hostname+ip already exists
        with self._lock:
            for existing in self._nodes.values():
                if (
                    existing.hostname == registration.hostname
                    and existing.ip_address == registration.ip_address
                ):
                    # Re-registration: update existing node
                    existing.status = NodeStatus.ONLINE
                    existing.resources = registration.resources
                    existing.labels = registration.labels
                    existing.last_heartbeat = datetime.utcnow()
                    existing.version = registration.version
                    logger.info(f"Re-registered node {existing.id} ({existing.hostname})")
                    return existing

            node = Node(
                hostname=registration.hostname,
                ip_address=registration.ip_address,
                port=registration.port,
                resources=registration.resources,
                labels=registration.labels,
                last_heartbeat=datetime.utcnow(),
                version=registration.version,
            )
            self._nodes[node.id] = node

        logger.info(f"Registered new node {node.id} ({node.hostname})")
        return node

    def get_node(self, node_id: str) -> Optional[Node]:
        """Get node by ID."""
        return self._nodes.get(node_id)

    def list_nodes(self, status: Optional[NodeStatus] = None) -> List[Node]:
        """List all registered nodes."""
        nodes = list(self._nodes.values())
        if status:
            nodes = [n for n in nodes if n.status == status]
        return sorted(nodes, key=lambda n: n.registered_at, reverse=True)

    def update_node(self, node_id: str, **kwargs) -> Optional[Node]:
        """Update node fields."""
        with self._lock:
            node = self._nodes.get(node_id)
            if not node:
                return None
            for key, value in kwargs.items():
                if hasattr(node, key):
                    setattr(node, key, value)
            self._nodes[node_id] = node
        return node

    def remove_node(self, node_id: str) -> bool:
        """Remove a node from the registry."""
        with self._lock:
            if node_id in self._nodes:
                del self._nodes[node_id]
                return True
        return False

    def get_available_nodes(self) -> List[Node]:
        """Return nodes that are online and have capacity for more jobs."""
        return [
            n
            for n in self._nodes.values()
            if n.status == NodeStatus.ONLINE
            and len(n.current_jobs) < n.max_concurrent_jobs
        ]


# Module-level singleton
_store: Optional[InMemoryStore] = None


def get_store() -> InMemoryStore:
    """Return the global store singleton."""
    global _store
    if _store is None:
        _store = InMemoryStore()
    return _store

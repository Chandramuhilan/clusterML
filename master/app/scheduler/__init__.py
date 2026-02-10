"""Job Scheduler - FIFO scheduling with resource matching.

The scheduler runs on a periodic loop. Each tick it:
1. Checks for timed-out nodes
2. Takes pending/queued jobs in FIFO order
3. Finds a worker node whose resources satisfy the job requirements
4. Assigns the job to that node (marks job SCHEDULED → RUNNING)
"""

import asyncio
import logging
from typing import Optional

from core.protocols.models import JobStatus, NodeStatus
from core.utils.resources import check_resources_fit
from master.app.jobs import JobManager
from master.app.nodes import NodeManager
from master.app.storage import InMemoryStore

logger = logging.getLogger(__name__)


class Scheduler:
    """FIFO scheduler with resource-aware node matching."""

    def __init__(
        self,
        store: InMemoryStore,
        job_manager: JobManager,
        node_manager: NodeManager,
        interval_seconds: float = 5.0,
    ):
        self.store = store
        self.job_manager = job_manager
        self.node_manager = node_manager
        self.interval = interval_seconds
        self._running = False
        self._task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the scheduler loop."""
        self._running = True
        self._task = asyncio.create_task(self._loop())
        logger.info(f"Scheduler started (interval={self.interval}s)")

    async def stop(self):
        """Stop the scheduler loop."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Scheduler stopped")

    async def _loop(self):
        """Main scheduling loop."""
        while self._running:
            try:
                self._tick()
            except Exception as e:
                logger.error(f"Scheduler tick error: {e}", exc_info=True)
            await asyncio.sleep(self.interval)

    def _tick(self):
        """Single scheduling pass."""
        # 1. Health-check nodes
        timed_out = self.node_manager.check_timeouts()
        if timed_out:
            logger.info(f"Timed out {len(timed_out)} nodes")

        # 2. Get queued jobs (FIFO order)
        pending = [
            j
            for j in self.store.list_jobs()
            if j.status in (JobStatus.PENDING, JobStatus.QUEUED)
        ]
        pending.sort(key=lambda j: j.created_at)

        if not pending:
            return

        # 3. Get available nodes
        available_nodes = self.store.get_available_nodes()
        if not available_nodes:
            logger.debug(f"{len(pending)} jobs queued but no nodes available")
            return

        # 4. Try to match each pending job to a node
        for job in pending:
            assigned = False
            for node in available_nodes:
                # Check resource fit
                avail_cpu = node.resources.cpu_cores
                avail_mem = node.resources.memory_total_mb - node.resources.memory_used_mb
                avail_gpu = node.resources.gpu_count - len(
                    [
                        j_id
                        for j_id in node.current_jobs
                        if self.store.get_job(j_id)
                        and self.store.get_job(j_id).spec.resources.gpu > 0
                    ]
                )

                fits, reason = check_resources_fit(
                    required_cpu=job.spec.resources.cpu,
                    required_memory=job.spec.resources.memory,
                    required_gpu=job.spec.resources.gpu,
                    available_cpu_cores=avail_cpu,
                    available_memory_mb=avail_mem,
                    available_gpu=avail_gpu,
                )

                if fits:
                    # Assign job to this node
                    self.job_manager.mark_running(job.id, node.id)
                    node.current_jobs.append(job.id)
                    self.store.update_node(node.id, current_jobs=node.current_jobs)

                    # Remove node from available if at capacity
                    if len(node.current_jobs) >= node.max_concurrent_jobs:
                        available_nodes.remove(node)

                    logger.info(
                        f"Scheduled job {job.id} ({job.name}) → node {node.id} ({node.hostname})"
                    )
                    assigned = True
                    break

            if not assigned:
                logger.debug(
                    f"No suitable node for job {job.id} ({job.name}), staying queued"
                )

    def trigger(self):
        """Manually trigger a scheduling pass (useful after job submission)."""
        self._tick()

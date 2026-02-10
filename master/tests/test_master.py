"""Tests for the ClusterML Master Orchestrator.

Covers: storage, node management, job management, scheduler, and API routes.
Run with: pytest master/tests/ -v
"""

import os
import sys
import pytest

# Ensure project root is on path
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from core.protocols.models import (
    JobCreate,
    JobSpec,
    JobStatus,
    NodeRegister,
    NodeStatus,
    ResourceInfo,
    ResourceRequirements,
    HeartbeatRequest,
    JobUpdate,
)
from core.utils.resources import parse_cpu, parse_memory, check_resources_fit
from master.app.storage import InMemoryStore
from master.app.nodes import NodeManager
from master.app.jobs import JobManager
from master.app.scheduler import Scheduler


# ── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def store():
    return InMemoryStore()


@pytest.fixture
def node_manager(store):
    return NodeManager(store, node_timeout_seconds=60)


@pytest.fixture
def job_manager(store):
    return JobManager(store)


@pytest.fixture
def sample_node_registration():
    return NodeRegister(
        hostname="worker-1",
        ip_address="192.168.1.10",
        port=8081,
        resources=ResourceInfo(
            cpu_cores=8,
            cpu_usage_percent=10.0,
            memory_total_mb=16384,
            memory_used_mb=2048,
            gpu_count=1,
            gpu_names=["RTX 3080"],
            gpu_memory_total_mb=10240,
            gpu_memory_used_mb=0,
        ),
        labels={"team": "ml", "gpu": "true"},
    )


@pytest.fixture
def sample_job_create():
    return JobCreate(
        name="test-training-job",
        labels={"team": "ml"},
        spec=JobSpec(
            image="pytorch/pytorch:2.0",
            command=["python", "train.py"],
            resources=ResourceRequirements(cpu="4", memory="8Gi", gpu=1),
        ),
    )


# ── Resource Parsing Tests ──────────────────────────────────────────────────

class TestResourceParsing:
    def test_parse_cpu_cores(self):
        assert parse_cpu("4") == 4.0

    def test_parse_cpu_millicores(self):
        assert parse_cpu("2500m") == 2.5

    def test_parse_memory_gi(self):
        assert parse_memory("16Gi") == 16384

    def test_parse_memory_mi(self):
        assert parse_memory("512Mi") == 512

    def test_parse_memory_g(self):
        assert parse_memory("2G") == 2000

    def test_check_resources_fit_ok(self):
        fits, reason = check_resources_fit("2", "4Gi", 1, 8, 16384, 2)
        assert fits is True

    def test_check_resources_fit_cpu_fail(self):
        fits, reason = check_resources_fit("16", "4Gi", 0, 8, 16384, 0)
        assert fits is False
        assert "CPU" in reason

    def test_check_resources_fit_gpu_fail(self):
        fits, reason = check_resources_fit("2", "4Gi", 2, 8, 16384, 1)
        assert fits is False
        assert "GPU" in reason


# ── Storage Tests ───────────────────────────────────────────────────────────

class TestInMemoryStore:
    def test_create_and_get_job(self, store, sample_job_create):
        job = store.create_job(sample_job_create)
        assert job.id is not None
        assert job.name == "test-training-job"
        assert job.status == JobStatus.PENDING

        retrieved = store.get_job(job.id)
        assert retrieved is not None
        assert retrieved.id == job.id

    def test_list_jobs_filters(self, store, sample_job_create):
        j1 = store.create_job(sample_job_create)
        store.update_job(j1.id, status=JobStatus.RUNNING)

        j2 = store.create_job(sample_job_create)

        running = store.list_jobs(status=JobStatus.RUNNING)
        assert len(running) == 1
        assert running[0].id == j1.id

        all_jobs = store.list_jobs()
        assert len(all_jobs) == 2

    def test_register_and_list_nodes(self, store, sample_node_registration):
        node = store.register_node(sample_node_registration)
        assert node.id is not None
        assert node.hostname == "worker-1"

        nodes = store.list_nodes()
        assert len(nodes) == 1

    def test_node_re_registration(self, store, sample_node_registration):
        n1 = store.register_node(sample_node_registration)
        n2 = store.register_node(sample_node_registration)
        assert n1.id == n2.id  # Same node
        assert len(store.list_nodes()) == 1

    def test_get_available_nodes(self, store, sample_node_registration):
        node = store.register_node(sample_node_registration)
        available = store.get_available_nodes()
        assert len(available) == 1

        # Fill capacity
        node.current_jobs = ["job-1", "job-2"]
        store.update_node(node.id, current_jobs=node.current_jobs)
        available = store.get_available_nodes()
        assert len(available) == 0


# ── Node Manager Tests ──────────────────────────────────────────────────────

class TestNodeManager:
    def test_register(self, node_manager, sample_node_registration):
        node = node_manager.register(sample_node_registration)
        assert node.status == NodeStatus.ONLINE
        assert node.hostname == "worker-1"

    def test_heartbeat_known_node(self, node_manager, sample_node_registration):
        node = node_manager.register(sample_node_registration)
        response = node_manager.heartbeat(
            HeartbeatRequest(
                worker_id=node.id,
                resources=sample_node_registration.resources,
                active_jobs=[],
            )
        )
        assert response.acknowledged is True

    def test_heartbeat_unknown_node(self, node_manager):
        response = node_manager.heartbeat(
            HeartbeatRequest(
                worker_id="nonexistent",
                resources=ResourceInfo(cpu_cores=4, memory_total_mb=8192),
            )
        )
        assert response.acknowledged is False


# ── Job Manager Tests ───────────────────────────────────────────────────────

class TestJobManager:
    def test_create_job(self, job_manager, sample_job_create):
        job = job_manager.create(sample_job_create)
        assert job.status == JobStatus.QUEUED
        assert job.name == "test-training-job"

    def test_cancel_job(self, job_manager, sample_job_create):
        job = job_manager.create(sample_job_create)
        cancelled = job_manager.cancel(job.id)
        assert cancelled.status == JobStatus.CANCELLED

    def test_cancel_completed_job_noop(self, job_manager, sample_job_create):
        job = job_manager.create(sample_job_create)
        job_manager.mark_completed(job.id, result={"accuracy": 0.95})
        cancelled = job_manager.cancel(job.id)
        assert cancelled.status == JobStatus.COMPLETED  # Unchanged

    def test_mark_running(self, job_manager, sample_job_create):
        job = job_manager.create(sample_job_create)
        running = job_manager.mark_running(job.id, "worker-abc")
        assert running.status == JobStatus.RUNNING
        assert running.worker_id == "worker-abc"
        assert running.started_at is not None

    def test_mark_failed(self, job_manager, sample_job_create):
        job = job_manager.create(sample_job_create)
        failed = job_manager.mark_failed(job.id, error="OOM killed")
        assert failed.status == JobStatus.FAILED
        assert failed.error == "OOM killed"

    def test_get_stats(self, job_manager, sample_job_create):
        j1 = job_manager.create(sample_job_create)
        j2 = job_manager.create(sample_job_create)
        job_manager.mark_running(j1.id, "w1")
        stats = job_manager.get_stats()
        assert stats.get("running", 0) == 1
        assert stats.get("queued", 0) == 1


# ── Scheduler Tests ─────────────────────────────────────────────────────────

class TestScheduler:
    def test_tick_assigns_job_to_node(
        self, store, job_manager, node_manager, sample_node_registration, sample_job_create
    ):
        scheduler = Scheduler(store, job_manager, node_manager, interval_seconds=1)

        # Register a node
        node_manager.register(sample_node_registration)

        # Create a job
        job = job_manager.create(sample_job_create)
        assert job.status == JobStatus.QUEUED

        # Run one scheduling tick
        scheduler._tick()

        # Job should now be RUNNING
        updated_job = job_manager.get(job.id)
        assert updated_job.status == JobStatus.RUNNING
        assert updated_job.worker_id is not None

    def test_tick_no_nodes_stays_queued(
        self, store, job_manager, node_manager, sample_job_create
    ):
        scheduler = Scheduler(store, job_manager, node_manager, interval_seconds=1)
        job = job_manager.create(sample_job_create)
        scheduler._tick()
        assert job_manager.get(job.id).status == JobStatus.QUEUED

    def test_tick_insufficient_resources(
        self, store, job_manager, node_manager, sample_job_create
    ):
        scheduler = Scheduler(store, job_manager, node_manager, interval_seconds=1)

        # Register a small node (no GPU)
        small_node = NodeRegister(
            hostname="tiny-worker",
            ip_address="192.168.1.20",
            resources=ResourceInfo(
                cpu_cores=2,
                memory_total_mb=4096,
                gpu_count=0,
            ),
        )
        node_manager.register(small_node)

        # Job requires GPU
        job = job_manager.create(sample_job_create)
        scheduler._tick()

        # Should remain queued (GPU requirement not met)
        assert job_manager.get(job.id).status == JobStatus.QUEUED

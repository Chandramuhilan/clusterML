"""API integration tests using FastAPI TestClient.

Run with: pytest master/tests/test_api.py -v
"""

import os
import sys

_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

import pytest
from fastapi.testclient import TestClient
from master.main import app


@pytest.fixture(autouse=True)
def reset_store():
    """Reset the global store between tests."""
    import master.app.storage as storage_mod
    storage_mod._store = None


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


class TestRootEndpoints:
    def test_health(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"

    def test_root(self, client):
        r = client.get("/")
        assert r.status_code == 200
        body = r.json()
        assert body["name"] == "ClusterML Master"
        assert "endpoints" in body

    def test_docs(self, client):
        r = client.get("/docs")
        assert r.status_code == 200


class TestNodesAPI:
    def test_register_node(self, client):
        payload = {
            "hostname": "test-worker",
            "ip_address": "10.0.0.5",
            "port": 8081,
            "resources": {
                "cpu_cores": 8,
                "memory_total_mb": 16384,
                "gpu_count": 1,
                "gpu_names": ["RTX 3080"],
                "gpu_memory_total_mb": 10240,
            },
            "labels": {"team": "ml"},
        }
        r = client.post("/api/v1/nodes", json=payload)
        assert r.status_code == 201
        body = r.json()
        assert body["hostname"] == "test-worker"
        assert body["status"] == "online"
        return body["id"]

    def test_list_nodes(self, client):
        # Register first
        self.test_register_node(client)
        r = client.get("/api/v1/nodes")
        assert r.status_code == 200
        assert len(r.json()) >= 1

    def test_cluster_status(self, client):
        self.test_register_node(client)
        r = client.get("/api/v1/nodes/status")
        assert r.status_code == 200
        body = r.json()
        assert body["total_nodes"] >= 1
        assert body["online_nodes"] >= 1

    def test_heartbeat(self, client):
        node_id = self.test_register_node(client)
        r = client.post(
            "/api/v1/nodes/heartbeat",
            json={
                "worker_id": node_id,
                "resources": {
                    "cpu_cores": 8,
                    "memory_total_mb": 16384,
                    "gpu_count": 1,
                },
                "active_jobs": [],
            },
        )
        assert r.status_code == 200
        assert r.json()["acknowledged"] is True

    def test_heartbeat_unknown_node(self, client):
        r = client.post(
            "/api/v1/nodes/heartbeat",
            json={
                "worker_id": "nonexistent-id",
                "resources": {"cpu_cores": 4, "memory_total_mb": 8192},
            },
        )
        assert r.status_code == 404


class TestJobsAPI:
    def _register_node(self, client):
        payload = {
            "hostname": "gpu-worker",
            "ip_address": "10.0.0.10",
            "resources": {
                "cpu_cores": 16,
                "memory_total_mb": 65536,
                "gpu_count": 4,
                "gpu_names": ["A100"] * 4,
                "gpu_memory_total_mb": 40960,
            },
        }
        return client.post("/api/v1/nodes", json=payload).json()["id"]

    def _submit_job(self, client):
        r = client.post(
            "/api/v1/jobs",
            json={
                "name": "mnist-train",
                "labels": {"framework": "pytorch"},
                "spec": {
                    "image": "pytorch/pytorch:2.0",
                    "command": ["python", "train.py"],
                    "resources": {"cpu": "4", "memory": "8Gi", "gpu": 1},
                },
            },
        )
        assert r.status_code == 201
        body = r.json()
        assert body["name"] == "mnist-train"
        return body["id"]

    def test_submit_job(self, client):
        job_id = self._submit_job(client)
        r = client.get(f"/api/v1/jobs/{job_id}")
        body = r.json()
        # No nodes registered so job stays queued
        assert body["status"] == "queued"

    def test_get_job(self, client):
        job_id = self._submit_job(client)
        r = client.get(f"/api/v1/jobs/{job_id}")
        assert r.status_code == 200
        assert r.json()["id"] == job_id

    def test_list_jobs(self, client):
        self._submit_job(client)
        r = client.get("/api/v1/jobs")
        assert r.status_code == 200
        assert len(r.json()) >= 1

    def test_cancel_job(self, client):
        job_id = self._submit_job(client)
        r = client.delete(f"/api/v1/jobs/{job_id}")
        assert r.status_code == 200
        assert r.json()["status"] == "cancelled"

    def test_get_job_logs(self, client):
        job_id = self._submit_job(client)
        r = client.get(f"/api/v1/jobs/{job_id}/logs")
        assert r.status_code == 200
        assert "logs" in r.json()

    def test_job_stats(self, client):
        self._submit_job(client)
        r = client.get("/api/v1/jobs/stats")
        assert r.status_code == 200

    def test_submit_and_schedule(self, client):
        """End-to-end: register node, submit job, verify scheduling."""
        self._register_node(client)
        job_id = self._submit_job(client)

        # After submission with a node available, scheduler should assign it
        r = client.get(f"/api/v1/jobs/{job_id}")
        body = r.json()
        # Status should be "running" (scheduler triggered on submit)
        assert body["status"] == "running"
        assert body["worker_id"] is not None

    def test_job_not_found(self, client):
        r = client.get("/api/v1/jobs/nonexistent")
        assert r.status_code == 404

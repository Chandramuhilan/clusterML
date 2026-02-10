"""Nodes API - REST endpoints for worker node management.

Endpoints:
    POST   /api/v1/nodes              - Register a new worker node
    GET    /api/v1/nodes              - List registered nodes
    GET    /api/v1/nodes/{id}         - Get node details
    DELETE /api/v1/nodes/{id}         - Unregister a node
    POST   /api/v1/nodes/heartbeat    - Worker heartbeat
"""

import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Query, status

from core.protocols.models import (
    HeartbeatRequest,
    HeartbeatResponse,
    Node,
    NodeRegister,
    NodeStatus,
    ClusterStatus,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# Injected at startup
_node_manager = None
_store = None


def init(node_manager, store):
    """Inject dependencies. Called at application startup."""
    global _node_manager, _store
    _node_manager = node_manager
    _store = store


@router.post("", response_model=Node, status_code=status.HTTP_201_CREATED)
async def register_node(registration: NodeRegister):
    """Register a worker node with the master."""
    node = _node_manager.register(registration)
    return node


@router.get("", response_model=List[Node])
async def list_nodes(
    status_filter: Optional[NodeStatus] = Query(None, alias="status"),
):
    """List all registered worker nodes."""
    return _node_manager.list_nodes(status=status_filter)


@router.get("/status", response_model=ClusterStatus)
async def cluster_status():
    """Get aggregated cluster status."""
    nodes = _node_manager.list_nodes()
    online_nodes = [n for n in nodes if n.status == NodeStatus.ONLINE]
    job_stats = _store.count_jobs_by_status()

    return ClusterStatus(
        total_nodes=len(nodes),
        online_nodes=len(online_nodes),
        total_jobs=sum(job_stats.values()),
        running_jobs=job_stats.get("running", 0),
        pending_jobs=job_stats.get("pending", 0) + job_stats.get("queued", 0),
        completed_jobs=job_stats.get("completed", 0),
        failed_jobs=job_stats.get("failed", 0),
        total_cpu_cores=sum(n.resources.cpu_cores for n in online_nodes),
        total_gpu_count=sum(n.resources.gpu_count for n in online_nodes),
        total_memory_mb=sum(n.resources.memory_total_mb for n in online_nodes),
    )


@router.get("/{node_id}", response_model=Node)
async def get_node(node_id: str):
    """Get details of a specific worker node."""
    node = _node_manager.get_node(node_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")
    return node


@router.delete("/{node_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_node(node_id: str):
    """Unregister a worker node."""
    if not _node_manager.remove_node(node_id):
        raise HTTPException(status_code=404, detail=f"Node {node_id} not found")


@router.post("/heartbeat", response_model=HeartbeatResponse)
async def heartbeat(request: HeartbeatRequest):
    """Process a worker heartbeat.

    Workers call this periodically to report health and receive job assignments.
    """
    response = _node_manager.heartbeat(request)
    if not response.acknowledged:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Worker {request.worker_id} not registered. Please re-register.",
        )
    return response

"""Node Management - handles registration, heartbeats, and health tracking."""

import logging
from datetime import datetime, timedelta
from typing import List, Optional

from core.protocols.models import (
    HeartbeatRequest,
    HeartbeatResponse,
    Node,
    NodeRegister,
    NodeStatus,
)
from master.app.storage import InMemoryStore

logger = logging.getLogger(__name__)


class NodeManager:
    """Manages worker node lifecycle: register, heartbeat, timeout."""

    def __init__(self, store: InMemoryStore, node_timeout_seconds: float = 90.0):
        self.store = store
        self.node_timeout = timedelta(seconds=node_timeout_seconds)

    def register(self, registration: NodeRegister) -> Node:
        """Register a worker node and return its full representation."""
        return self.store.register_node(registration)

    def heartbeat(self, request: HeartbeatRequest) -> HeartbeatResponse:
        """Process a heartbeat from a worker.

        Updates the node's last-seen timestamp and resource snapshot.
        Returns any pending job assignments.
        """
        node = self.store.get_node(request.worker_id)
        if node is None:
            logger.warning(f"Heartbeat from unknown worker {request.worker_id}")
            return HeartbeatResponse(acknowledged=False)

        self.store.update_node(
            request.worker_id,
            last_heartbeat=datetime.utcnow(),
            resources=request.resources,
            current_jobs=request.active_jobs,
            status=NodeStatus.ONLINE,
        )
        logger.debug(f"Heartbeat from {node.hostname} ({request.worker_id})")

        return HeartbeatResponse(acknowledged=True)

    def check_timeouts(self) -> List[str]:
        """Mark nodes as offline if heartbeat has timed out.

        Returns list of node IDs that were marked offline.
        """
        timed_out: List[str] = []
        now = datetime.utcnow()
        for node in self.store.list_nodes(status=NodeStatus.ONLINE):
            if node.last_heartbeat and (now - node.last_heartbeat) > self.node_timeout:
                self.store.update_node(node.id, status=NodeStatus.OFFLINE)
                logger.warning(f"Node {node.id} ({node.hostname}) timed out")
                timed_out.append(node.id)
        return timed_out

    def get_node(self, node_id: str) -> Optional[Node]:
        return self.store.get_node(node_id)

    def list_nodes(self, status: Optional[NodeStatus] = None) -> List[Node]:
        return self.store.list_nodes(status)

    def remove_node(self, node_id: str) -> bool:
        return self.store.remove_node(node_id)
